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


def test_requirement_req_placeholder_keeps_requirement_scaffold_until_replaced() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    text = (
        "---\n"
        "種別: 要件定義書（Issue）\n"
        '状態: "approved"\n'
        "---\n\n"
        "# Requirement\n\n"
        "## 目的\n"
        "- Concrete objective.\n\n"
        "| ID | 内容 | 根拠 |\n"
        "|---|---|---|\n"
        "| REQ-XXX | 必要な数だけ連番で追加する | issue discussion |\n"
    )

    assert workflow_state.classify_requirement_text(text) == "scaffold"


def test_requirement_contract_placeholder_keeps_requirement_scaffold_until_replaced() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    text = (
        "---\n"
        "種別: 要件定義書（Issue）\n"
        '状態: "approved"\n'
        "---\n\n"
        "# Requirement\n\n"
        "## 目的\n"
        "- Concrete objective.\n\n"
        "## 制約\n"
        "- CON-...: concrete contract still needs to be filled before execution.\n"
    )

    assert workflow_state.classify_requirement_text(text) == "scaffold"


def test_report_evidence_gate_blocks_missing_report_for_strict_profile() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(None, "strict")

    assert result.status == "blocked"
    assert result.reason_code == "report-evidence-missing"


def test_report_evidence_gate_blocks_missing_report_for_lite_profile() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(None, "lite")

    assert result.status == "blocked"
    assert result.reason_code == "report-evidence-missing"


def test_report_evidence_gate_blocks_scaffold_marker_in_report() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| lite | not applicable | not applicable | lite not applicable reason | pass / fail / blocked | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "lite",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-evidence-scaffold"


def test_report_evidence_gate_requires_lite_grade_not_applicable_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "lite",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_accepts_lite_grade_not_applicable_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| lite | not applicable | not applicable | lite not applicable reason | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "lite",
    )

    assert result.status == "pass"
    assert result.reason_code == "report-evidence-valid"


def test_report_evidence_gate_requires_fresh_spec_review_for_standard_plus() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "| strict | manual fallback | unavailable | manual authoring fallback with source inspection and residual risk | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | pending | pending | no | pending | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-review-missing"


def test_report_evidence_gate_rejects_failed_spec_authoring_gate_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | fail | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-authoring-gate-invalid"


def test_report_evidence_gate_rejects_blocking_spec_authoring_gate_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | yes | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-authoring-gate-invalid"


def test_report_evidence_gate_requires_delegated_draft_evidence_section_for_standard_plus() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | manual fallback | unavailable | manual authoring fallback with source inspection and residual risk | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-evidence-incomplete"


def test_report_evidence_gate_requires_eal_adoption_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| ID | adoption_status | source | target | rationale | evidence | next_action |\n"
        "|---|---|---|---|---|---|---|\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated | none | none | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-eal-missing"


def test_report_evidence_gate_requires_delegated_draft_evidence_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス | 参照元 | 予定反映先 | 採用状態 | 反映先 | 差分ガード結果 | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果 | 昇格判断 |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "delegated-draft-evidence-missing"


def test_report_evidence_gate_rejects_ineligible_delegated_draft_state() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| role | scope | draft path | source paths | intended targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | rejected | [] | not_run | rejected | all | none | pass | blocked |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "delegated-draft-evidence-missing"


def test_report_evidence_gate_rejects_draft_path_without_adoption_provenance() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| role | scope | draft path | source paths | intended targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | unreviewed | [] | not_run | requested | none | none | pass | pending |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "delegated-draft-evidence-missing"


def test_report_evidence_gate_rejects_delegated_draft_without_matching_eal_reference() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | requirement.md | unrelated rationale | requirement.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| role | scope | draft path | source paths | intended targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated | none | none | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "delegated-draft-evidence-missing"


def test_report_evidence_gate_rejects_stale_spec_reviewer_even_when_state_passed() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated; not promotion evidence | none | none | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | stale | passed | no | execute approved plan | stale row |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-review-missing"


def test_report_evidence_gate_rejects_whole_file_fresh_pass_shortcut() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "review_status: pass\n"
        "fresh reviewer evidence exists elsewhere, but not on the spec-reviewer row.\n\n"
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated; not promotion evidence | none | none | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | pending | pending | no | pending | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-review-missing"


def test_report_evidence_gate_requires_fresh_spec_review_in_reviewer_gate_section() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | spec-reviewer | fresh | pass |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | stale | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-review-missing"


def test_report_evidence_gate_requires_spec_reviewer_role() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | qa-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-review-missing"


def test_report_evidence_gate_blocks_unresolved_eal_entries() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | stale | source | target | rationale | evidence | re-review |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated; not promotion evidence | none | none | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-eal-unresolved"


def test_report_evidence_gate_blocks_localized_unresolved_eal_entries() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | stale（stale） | source | target | rationale | evidence | re-review |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-eal-unresolved"


def test_report_evidence_gate_requires_specialist_or_fallback_for_strict_profile() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_requires_specialist_or_skip_reason_for_standard_profile() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_stray_manual_fallback_phrase() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale mentions manual authoring fallback | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_manual_fallback_without_grade_specialist_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | partially_adopted | source | design.md | rationale | discussions/draft.md | pass |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated; not promotion evidence | none | prior reviewer evidence missing; resolved by manual authoring fallback D-003 | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_eal_reference_to_target_without_draft_path() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | partially_adopted | source | design.md | rationale | design.md | pass |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated; not promotion evidence | none | prior reviewer evidence missing; resolved by manual authoring fallback D-003 | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "delegated-draft-evidence-missing"


def test_report_evidence_gate_rejects_eal_reference_from_rejected_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | rejected | source | design.md | rejected rationale | discussions/draft.md | blocked |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| system-architect | iss-00301 | discussions/draft.md | active docs | design.md | partially_adopted | design.md | orchestrator inspection pass | source input integrated; not promotion evidence | none | prior reviewer evidence missing; resolved by manual authoring fallback D-003 | pass | execute manual-authored canonical docs |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "delegated-draft-evidence-missing"


def test_report_evidence_gate_rejects_specialist_names_without_usage_or_evidence() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | system-architect / implementation-planner | skipped | none | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_not_used_specialist_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | system-architect / implementation-planner | not used | system-architect not used; no explicit skip reason | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_cross_profile_grade_row() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_strict_skip_reason_without_fallback() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_used_specialist_without_evidence() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | system-architect / implementation-planner | used | none | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_failed_grade_reviewer_verdict() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | system-architect / implementation-planner | used | discussions/fresh-draft.md | fail | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_negated_grade_reviewer_pass_phrase() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | system-architect / implementation-planner | used | discussions/fresh-draft.md | did not pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_stale_reviewer_gate_with_pass_elsewhere() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | target | rationale | evidence | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| step | gate name | reviewer role | freshness | state | risk acceptance | promotion decision | notes |\n"
        "| planning | planning spec-review | spec-reviewer | stale | pending | pass | execute approved plan | later note says fresh |\n",
        "standard",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-spec-review-missing"


def test_report_evidence_gate_rejects_lite_failed_grade_verdict() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | source | design.md | rationale | discussions/draft.md | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | adopted | pass | no | execute approved plan |\n"
        "| design | docs | none | adopted | pass | no | execute approved plan |\n"
        "| plan | docs | none | adopted | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| lite | not applicable | not applicable | lite not applicable reason | fail | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "lite",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_accepts_standard_skip_reason_in_grade_specialist_table() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | fixture | requirement/design/plan | source input only | test fixture | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| standard | system-architect / implementation-planner | skipped | skip reason: existing pattern sufficient | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "standard",
    )

    assert result.status == "pass"
    assert result.reason_code == "report-evidence-valid"


def test_report_evidence_gate_accepts_strict_used_specialist_with_evidence() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | fixture | requirement/design/plan | source input only | test fixture | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | system-architect / implementation-planner | used | discussions/strict-design-draft.md | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "pass"
    assert result.reason_code == "report-evidence-valid"


def test_report_evidence_gate_accepts_strict_fallback_in_grade_specialist_table() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | partially_adopted | fixture | requirement/design/plan | source input only | test fixture | pass |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| strict | manual fallback | unavailable | manual authoring fallback with source inspection and residual risk | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "strict",
    )

    assert result.status == "pass"
    assert result.reason_code == "report-evidence-valid"


def test_report_evidence_gate_rejects_critical_fallback_without_approval() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | fixture | requirement/design/plan | source input only | test fixture | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| critical | manual fallback | unavailable | manual fallback with strong evidence but no approval | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "critical",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_critical_fallback_with_negated_approval() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | fixture | requirement/design/plan | source input only | test fixture | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| critical | manual fallback | unavailable | manual fallback with no approval but risk acceptance | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "critical",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_rejects_critical_fallback_with_negated_explicit_approval() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | fixture | requirement/design/plan | source input only | test fixture | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| critical | manual fallback | unavailable | manual fallback with no explicit approval but risk acceptance | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "critical",
    )

    assert result.status == "blocked"
    assert result.reason_code == "report-specialist-evidence-missing"


def test_report_evidence_gate_accepts_critical_fallback_with_approval_and_risk_acceptance() -> None:
    _runbook_module, workflow_state = _workflow_modules()

    result = workflow_state.evaluate_report_evidence_gate(
        "## 証跡採用台帳（Evidence Adoption Ledger / 必須）\n"
        "| EAL-001 | adopted | fixture | requirement/design/plan | source input only | test fixture | none |\n\n"
        "## 仕様 authoring ゲート（Spec Authoring Gate / 必須）\n"
        "| requirement | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| design | docs | none | manual authoring candidate | pass | no | execute approved plan |\n"
        "| plan | docs | none | manual authoring candidate | pass | no | execute approved plan |\n\n"
        "## 委任ドラフト証跡（Delegated Draft Evidence / 必須）\n"
        "| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | 該当なし | none | pass | execute approved plan |\n\n"
        "#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）\n"
        "| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |\n"
        "|---|---|---|---|---|---|\n"
        "| critical | manual fallback | unavailable | explicit approval for manual fallback with strong evidence and risk acceptance | pass | ready |\n\n"
        "#### レビューゲート状態（Reviewer Gate Status）\n"
        "| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | note |\n",
        "critical",
    )

    assert result.status == "pass"
    assert result.reason_code == "report-evidence-valid"
