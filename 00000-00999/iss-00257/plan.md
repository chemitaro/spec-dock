---
種別: 実装計画書（Issue）
ID: "iss-00257"
タイトル: "Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening"
関連GitHub: ["#257"]
状態: "review-needed"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
authorized_profile: "standard"
---

# iss-00257 Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening — Issue 実装計画書

## 0. 計画の位置づけ

この計画は、reviewer-passed requirement と reviewer-passed design を、実装・テスト・report evidence へ落とす実行契約である。実装そのものはこの文書の spec-reviewer pass 後に開始する。

## 1. Readiness

| 入力 | 状態 | 備考 |
|---|---|---|
| `requirement.md` | concrete / reviewed | spec-reviewer pass |
| `design.md` | concrete / reviewed | spec-reviewer pass |
| `report.md` | evidence ledger target | final authoring evidence を記録する |
| `assurance classify --stage requirement` | completed | `authorized_profile: standard` |
| plan spec-reviewer gate | pending | この文書のレビューで実施 |

## 2. Allowed / Forbidden Change Surface

### Allowed

| Surface | Paths |
|---|---|
| Review instruction assets | `.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/codex-review-instructions.md` |
| Observation runtime | `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` |
| Merge-preparer skill assets | `.agents/skills/github-pr-merge-preparer/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` |
| Repair-batch template | `spec-dock/templates/discussions/pr-repair-batch.md`; `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md` |
| Tests | `tests/unit/infra/test_init_update.py` |
| Issue-local docs/evidence | `spec-dock/active/issue/{requirement.md,design.md,plan.md,report.md,discussions/*.md}` |

### Forbidden

| Target | Reason |
|---|---|
| `spec-dock/active/epic/*` and parent `epic-00224` docs | User instructed this Issue must not edit parent Epic docs |
| Runtime `root_cause_family` parser / JSON / stalled logic | User selected docs/LLM judgement scope only |
| GitHub PR merge / branch deletion / conversation resolution | Out of Issue scope |
| Broad workflow policy docs unrelated to this Issue | Keep scope issue-local |

## 3. Spec-Locked Closure Index

| Closure ID | Requirement | Design | Close condition | Verification |
|---|---|---|---|---|
| CLOS-001 | AC-001 | DES-001 | Review instruction defines P0/P1 blocking and P2/P3 reportable non-blocking, and removes old "do not report P2/P3" policy | test assertion or text inspection |
| CLOS-002 | AC-002 | DES-002 | P2 protected-domain + machine-evidence produces non-blocking follow-up, not `promoted_blocker` | focused unit test |
| CLOS-003 | AC-003 | DES-002 | P0/P1 findings still produce blockers and repair next action | existing focused unit tests |
| CLOS-004 | AC-004 | DES-003 | P2/P3-only clean state can reach `blocker_policy_no_action` / merge-prepared without repair loop | existing/updated focused unit test |
| CLOS-004A | AC-004 | DES-003, DES-004 | Terminal P2/P3-only state does not trigger repo-persistent repair batch update, commit/push, re-review request, or another autonomous repair loop | focused test where feasible plus text/runtime inspection tied to merge-preparer and repair-batch surfaces |
| CLOS-005 | AC-005 | DES-003 | `CHANGES_REQUESTED` / unresolved / collection gates remain separate from severity policy | existing focused unit tests / inspection |
| CLOS-006 | AC-006 | DES-004 | Merge-preparer and repair-batch docs separate P0/P1 repair from P2/P3 terminal report and keep `root_cause_family` docs-only | text inspection / tests if asset assertions exist |
| CLOS-007 | AC-007 | DES-005 | Provider/dogfooding mirrors match after updates | existing parity tests / `cmp` |
| CLOS-008 | AC-008 | DES-006 | Parent Epic docs are untouched | `git diff -- spec-dock/active/epic` and status inspection |
| CLOS-009 | AC-009 | DES-007 | Issue Planning dogfooding notes are recorded and adopted into report | report/discussion inspection |

## 4. 実装ステップ

### S00: Authoring evidence gate

- Owner: main orchestrator.
- Purpose: Record that requirement and design phase reviews passed before implementation.
- Actions:
  - Update `report.md` with requirement/design/plan reviewer gate evidence.
  - Explicitly mark the accidental no-op reviewer as not adopted.
  - Keep dogfooding notes about workflow friction in `discussions/`.
- Verification:
  - `rg -n "requirement authoring review|design authoring review|plan authoring review|not adopted" spec-dock/active/issue/report.md`
- Closures: CLOS-009.

### S10: Markdown policy assets

- Owner: dev-coder or doc-writer, depending on execution delegation.
- Purpose: Make human/LLM-facing PR review and merge-preparer policy match the accepted severity contract.
- Actions:
  - Update review instruction asset pair.
  - Update merge-preparer skill asset pair.
  - Update repair-batch template pair.
  - Prefer bundle text where it matches accepted scope, but adjust if it implies runtime `root_cause_family` contract beyond Option B.
- Red / alternative:
  - Existing asset tests expecting old phrases should fail or require update.
- Verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_176_s05b or issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing"`
  - Direct `cmp` for any updated mirror pair if a test failure points to parity.
- Closures: CLOS-001, CLOS-006, CLOS-007.

### S20: Runtime blocker policy

- Owner: dev-coder.
- Purpose: Make observation blocker policy P0/P1-only while retaining P2/P3 metadata.
- Actions:
  - Update `pr_review_snapshot.py` pair.
  - Remove P2 protected-domain + machine-evidence promotion.
  - Ensure blocker filtering is P0/P1-only.
  - Preserve existing platform gate separation and no-action path.
- Red:
  - Existing protected-domain + machine-evidence P2 promotion test should fail until expectation and implementation are updated.
- Verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_232"`
- Closures: CLOS-002, CLOS-003, CLOS-004, CLOS-004A, CLOS-005, CLOS-007.

### S30: Test updates and focused verification

- Owner: dev-coder, then code-reviewer / qa-reviewer if delegated.
- Purpose: Align tests with the new policy without dropping existing protections.
- Actions:
  - Update old instruction text assertions.
  - Update P2 protected-domain + machine-evidence expectation to non-blocking follow-up.
  - Keep P1/P0, CHANGES_REQUESTED, priorityless, and parity coverage.
  - Add or preserve verification that a terminal P2/P3-only clean state does not cause repo-persistent repair-batch persistence, commit/push, re-review request, or another autonomous repair loop. If this cannot be fully asserted in unit tests because the boundary is instruction/template-driven, record explicit inspection evidence for the affected merge-preparer skill and repair-batch template in `report.md`.
- Focused command:
  ```bash
  uv run pytest tests/unit/infra/test_init_update.py -k "issue_176_s05b or issue_232 or issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing or issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint"
  ```
- Broader fallback:
  ```bash
  uv run pytest tests/unit/infra/test_init_update.py
  ```
- Closures: CLOS-001 through CLOS-007.

### S40: Terminal no-mutation boundary verification

- Owner: dev-coder for executable checks; main orchestrator for final evidence integration.
- Purpose: Close the specific P2/P3-only no-mutation obligation from AC-004.
- Actions:
  - Verify that observation runtime treats P2/P3-only findings as `blocker_policy_no_action` / merge-prepared when other gates are clean.
  - Verify that merge-preparer instructions do not direct branch mutation, repo-persistent batch updates, pushes, or re-review requests solely for terminal P2/P3-only findings.
  - Verify that repair-batch template says persistent batches are for blocking repair / blocking triage, not non-blocking P2/P3-only follow-ups.
  - Record in `report.md` whether each no-mutation boundary was covered by unit test, text inspection, or runtime inspection.
- Verification:
  ```bash
  uv run pytest tests/unit/infra/test_init_update.py -k "issue_232"
  rg -n "P2/P3|non-blocking|re-review|push|persistent|repair batch|blocker_policy_no_action" .agents/skills/github-pr-merge-preparer/SKILL.md spec-dock/templates/discussions/pr-repair-batch.md
  ```
- Required report evidence:
  - `batch_persistence`: no repo-persistent repair-batch update for P2/P3-only terminal findings.
  - `commit_push`: no commit or push solely for P2/P3-only terminal findings.
  - `re_review`: no re-review request solely for P2/P3-only terminal findings.
  - `repair_loop`: no autonomous repair loop solely for P2/P3-only terminal findings.
- Closures: CLOS-004A, CLOS-006.

### S90: Docs / report impact

- Owner: main orchestrator for issue-local docs, doc-writer only if persistent non-issue docs become necessary.
- Purpose: Close documentation and dogfooding evidence without expanding scope.
- Actions:
  - Update `report.md` with observed implementation evidence.
  - Update dogfooding discussion if Issue Planning workflow shows additional friction or bug.
  - Confirm parent Epic docs remain untouched.
- Verification:
  ```bash
  git diff -- spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/requirement.md spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/design.md spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/plan.md
  git status --short
  ```
- Closures: CLOS-008, CLOS-009.

### S99: Final quality gate

- Owner: main orchestrator coordinating reviewers.
- Purpose: Verify implementation, docs, and review gates before commit/PR handoff.
- Actions:
  - Run final focused tests.
  - Run broader unit lane if risk warrants:
    ```bash
    uv run pytest tests/unit
    ```
  - Run:
    ```bash
    ./spec-dock/scripts/spec-dock validate
    ./spec-dock/scripts/spec-dock assurance verify
    ```
  - Obtain final spec/code/QA review status or record explicit fallback.
  - Commit focused changes after successful gates.
- Closures: all CLOS.

## 5. Behavior Backlog

| Behavior ID | Step | Behavior | Closures | Status |
|---|---|---|---|---|
| B-001 | S10 | Reviewer instruction reports all severities but blocks only P0/P1 | CLOS-001 | planned |
| B-002 | S20 | P2 protected-domain + machine-evidence remains non-blocking metadata | CLOS-002 | planned |
| B-003 | S20 | P0/P1 blocker path remains intact | CLOS-003 | planned |
| B-004 | S20/S40 | P2/P3-only clean terminal state avoids repair mutation | CLOS-004, CLOS-004A | planned |
| B-005 | S20 | Platform/human gates remain separate | CLOS-005 | planned |
| B-006 | S10 | Merge-preparer and repair-batch express blocking repair boundary | CLOS-006 | planned |
| B-007 | S10-S30 | Provider/dogfooding mirrors remain in sync | CLOS-007 | planned |
| B-008 | S90 | Parent Epic docs remain untouched | CLOS-008 | planned |
| B-009 | S00/S90 | Issue Planning dogfooding evidence is recorded | CLOS-009 | planned |

## 6. Stop Conditions

- A needed change touches parent `epic-00224` docs.
- A needed change requires runtime `root_cause_family` first-class contract.
- A test failure suggests P0/P1 blockers are no longer blocking.
- GitHub platform state mutation becomes necessary.
- Reviewer finds requirement/design/plan gap that changes AC or scope.

## 7. Report Evidence Requirements

`report.md` must include:

- Evidence Adoption Ledger entries for research, interviews, dogfooding, classify/compose command outputs, and all spec-reviewer passes.
- Spec Authoring Gate rows showing requirement, design, and plan review state.
- Test evidence for each closure ID.
- Diff evidence proving parent Epic docs were not edited. Use the real parent Epic doc paths, not only `spec-dock/active/epic` symlinks:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/requirement.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/design.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/plan.md`
- Final commit candidate gate after implementation and verification.

## 8. Implementation Handoff Summary

The implementation should be a small, focused policy update:

1. Update three Markdown asset pairs to express severity-aware review / repair policy.
2. Update two runtime mirror files so only P0/P1 are semantic blockers.
3. Update focused unit tests and mirror parity assertions.
4. Preserve current `blocker_fingerprint` contract and platform gate separation.
5. Leave parent Epic docs untouched.
