---
種別: draft-design
ID: "20260620t024411z-draft-design"
タイトル: "Carryover observation design"
status: proposed
created_by_role: system-architect
scope_id: iss-00219
source_paths:
  - "spec-dock/active/context-pack.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/issue/discussions/20260619t164615z-research-carryover-observation-source-analysis.md"
  - "spec-dock/active/issue/discussions/20260619t164616z-interview-carryover-incomplete-stop-policy.md"
  - "spec-dock/active/issue/discussions/20260619t221823z-disc-carryover-review-completion-policy-synthesis.md"
  - "spec-dock/active/issue/discussions/20260620t010354z-interview-carryover-unknown-status-reason-naming.md"
  - ".agents/skills/github-pr-observation/SKILL.md"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py"
  - "tests/unit/infra/test_init_update.py"
intended_targets:
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Carryover observation design evidence

This is delegated architecture evidence only. It is not canonical `design.md`, does not claim adoption, and does not authorize implementation.

## 1. Requirement Coverage

- AC-001 is covered by separating current review lifecycle from carryover actionable inventory: guard-under, carryover-only, missing-completion remains non-terminal `pending` / `wait_or_resume` / `observation_complete=false`.
- AC-002 is covered by preserving immediate `human_gate` / `address_review_feedback` for current selected unresolved threads and current selected changes requested.
- AC-003 is covered by allowing carryover-only missing-completion to become `review_completion_unknown` only after latency guards are satisfied, with `post_unknown_fresh_audit_required=true`.
- AC-004 is covered by treating trusted current completion plus carryover unresolved as terminal feedback work: `human_gate` / `address_review_feedback` / `carryover_non_outdated_unresolved_thread`.
- AC-005 is covered by applying the same state taxonomy to snapshot and wait classification.
- AC-006 is covered by updating skill docs to describe the two-axis model and by correcting the `review_completion_unknown` definition from "actionable review inventory empty" to "current-boundary selected actionable feedback empty".

Source requirement revision used: `iss-00219` requirement, `最終更新: "2026-06-20"`, `状態: "draft"`.

## 2. Existing Context Findings

- `pr_review_snapshot.py` already collects the necessary inventory split:
  - current selected unresolved: `selected_unresolved_thread_ids`, `current_selected_unresolved_count`
  - carryover non-outdated unresolved: `carryover_unresolved_thread_ids`, `carryover_unresolved_count`
  - combined actionable inventory: `actionable_unresolved_thread_ids`, `actionable_unresolved_count`
- The bug is in classification, not primarily collection. Both `pr_observation_snapshot.py` and `pr_observation_wait.py` have an `actionable_unresolved_reason(...)` helper that collapses current selected blockers and carryover-only inventory into one terminal reason.
- Snapshot currently returns terminal `human_gate` / `address_review_feedback` whenever CI is passed and `actionable_reason` exists, before checking `missing_current_completion_signal`.
- Wait currently returns terminal `human_gate` / `address_review_feedback` under the same condition, and `is_review_completion_unknown_candidate(...)` rejects all actionable inventory, including carryover-only inventory.
- Existing tests around Issue 187 intentionally established that non-outdated carryover is actionable inventory. The new design must preserve that safety while changing when carryover-only inventory becomes terminal.

## 3. Design Decisions

- Use a two-axis decision model:
  - `decision.status_reason` describes the current review lifecycle / terminal reason.
  - carryover counts and IDs describe actionable inventory that may exist independently of the current review lifecycle.
- Do not make carryover-only inventory a terminal review-feedback stop while `completion_signal="none"` and the latency guard is not satisfied.
- Use existing `review_completion_unknown` after latency guard satisfaction, even when carryover exists. Carryover presence must remain visible through structured inventory fields.
- Add `decision.actionable_inventory_reason` as an optional compatibility-friendly field when actionable inventory exists but should not own `status_reason`.
  - Recommended value for carryover-only inventory: `carryover_non_outdated_unresolved_thread`.
  - Existing counts/IDs remain sufficient for older consumers; this field is an affordance for downstream branching and reports.
- Keep fallback issue comments out of scope for this issue. `fallback_issue_comment` remains low-confidence and does not become trusted completion here.
- Keep CI/head blockers ahead of review lifecycle classification.

## 4. Alternatives Considered

- Carryover-only immediate terminal `address_review_feedback`: rejected because it preserves the Issue 219 premature stop.
- Carryover audit-only / non-actionable: rejected because it hides real GitHub unresolved, non-outdated review threads and violates the Issue 187 safety contract.
- New status reason such as `current_review_completion_unknown_with_carryover_unresolved`: rejected for now because it fragments the reason taxonomy. The adopted naming evidence favors existing `review_completion_unknown` with carryover as a separate axis.
- Rely only on existing counts/IDs and add no field: acceptable but weaker. Counts/IDs are enough for compatibility, but `decision.actionable_inventory_reason` makes the split explicit without changing existing top-level next action semantics.

## 5. Boundary / Contract Model

State classification table:

| Scenario | Preconditions | Output family | `decision.status_reason` | Inventory contract |
| --- | --- | --- | --- | --- |
| Guard-under carryover-only | CI passed, head matched, current selected unresolved 0, selected changes requested none, `completion_signal="none"`, carryover count > 0, latency guard false | non-terminal wait/resume | `missing_current_completion_signal` | Keep carryover IDs/counts; set `actionable_inventory_reason="carryover_non_outdated_unresolved_thread"` |
| Guard-satisfied carryover-only | Same as above, but latency guard true | non-pass human gate | `review_completion_unknown` | Keep carryover IDs/counts; `post_unknown_fresh_audit_required=true`; optional inventory reason preserved |
| Current selected blocker | Current selected unresolved thread or current selected changes requested exists | terminal feedback handling | `current_selected_unresolved_thread` or `current_selected_changes_requested` | Carryover may also be listed, but current selected reason wins |
| Trusted completion + carryover | `completion_signal="submitted_pull_request_review"`, no current selected blocker, carryover count > 0 | terminal feedback handling | `carryover_non_outdated_unresolved_thread` | Carryover IDs/counts are the actionable feedback surface |
| Fallback issue comment | `completion_signal="fallback_issue_comment"` or low-confidence fallback present | non-pass wait/resume human gate | `fallback_issue_comment_low_confidence` | Do not promote fallback to trusted completion in this issue |
| CI/head blockers | stale head, draft/non-open PR, CI failed/pending/running/none, blocking permission/collection limitation | existing blocker output | existing CI/head/limitation reason | Carryover policy must not override CI/head priority |

## 6. Dependency Analysis

- `pr_review_snapshot.py` is upstream of both snapshot and wait. It should remain the collector/source of inventory fields.
- `pr_observation_snapshot.py` depends on review snapshot output and owns one-shot classification. Its classification must stop using combined actionable inventory as a precondition for immediate terminal feedback.
- `pr_observation_wait.py` depends on snapshot output across polling and owns latency guard behavior. It must distinguish:
  - current selected actionable feedback
  - carryover-only actionable inventory
  - unknown candidate eligibility
- `tests/unit/infra/test_init_update.py` is the regression surface for installed assets and runtime script behavior.
- Provider-side source under `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/...` is the implementation authority; `.agents/...` is the dogfooding mirror inspected in this draft.

## 7. Source of Record

- Canonical issue requirement is `spec-dock/active/issue/requirement.md`.
- Evidence sources are the research, interview, and synthesis docs listed in front matter.
- Runtime implementation source of record should be provider-side:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- Dogfooding mirror `.agents/...` should be updated only through the project’s normal scaffold/update path or deliberately mirrored as part of verification.

## 8. Data Flow / Domain Model / Interface Contract

Data flow:

```text
GitHub APIs
  -> pr_review_snapshot.py
       emits current selected feedback + carryover inventory + completion signal
  -> pr_observation_snapshot.py
       classifies one-shot observation using current lifecycle first
  -> pr_observation_wait.py
       repeats snapshots, applies quiet/latency/timeout, emits final JSON
  -> downstream merge-preparer / maintainer
       reads status reason and inventory as separate axes
```

Interface contract:

- Preserve existing fields:
  - `decision.status`
  - `decision.status_reason`
  - `decision.recommended_next_action`
  - `decision.observation_complete`
  - `decision.current_selected_unresolved_count`
  - `decision.current_selected_unresolved_thread_ids`
  - `decision.carryover_unresolved_count`
  - `decision.carryover_unresolved_thread_ids`
  - `decision.actionable_unresolved_count`
  - `decision.actionable_unresolved_thread_ids`
  - `decision.completion_signal`
- Add optional field:
  - `decision.actionable_inventory_reason`
  - Suggested values:
    - `carryover_non_outdated_unresolved_thread`
    - `current_selected_unresolved_thread` only if implementation wants symmetry; not required because current selected already owns `status_reason`.
- Do not add a new top-level status for this issue.
- Do not treat `selected_unresolved_count == 0` as no review work.
- Do not make `review_completion_unknown` a pass or merge-ready result.

Snapshot vs wait consistency plan:

- Snapshot must no longer turn guard-under carryover-only missing-completion into terminal `address_review_feedback`.
- Wait must use the same classification meaning, with the only wait-specific addition being latency guard promotion to `review_completion_unknown`.
- Prefer small shared helper semantics in both files:
  - `current_selected_actionable_reason(decision)`
  - `carryover_inventory_reason(decision)`
  - `has_current_selected_blocker(decision)`
  - `has_carryover_inventory(decision)`
- If helpers are duplicated rather than extracted, tests must cover snapshot and wait versions for the same matrix.

## 9. File / Module Change Plan

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/
|-- SKILL.md
|   `-- change: document two-axis lifecycle/inventory contract and revised review_completion_unknown definition
`-- scripts/lib/
    |-- pr_observation_snapshot.py
    |   `-- change: split current selected blocker from carryover-only inventory in classify_snapshot
    |-- pr_observation_wait.py
    |   `-- change: split actionable helpers, allow carryover-only unknown candidate, preserve inventory reason
    `-- pr_review_snapshot.py
        `-- likely no collection change; only add optional inventory reason here if centralizing field emission is simpler

tests/unit/infra/test_init_update.py
`-- change: add Issue 219 regression cases and adjust Issue 187 carryover terminal expectation where the new contract supersedes it

.agents/skills/github-pr-observation/
`-- dogfooding mirror: inspect/update after provider source changes; not the implementation authority
```

Implementation note: if `decision.actionable_inventory_reason` is added in `pr_review_snapshot.py`, both snapshot and wait get the same raw field. If added in classifiers, both files must update fingerprints consistently when mutating `decision`.

## 10. Migration / Compatibility / Rollback

- Compatibility:
  - Existing consumers that read counts/IDs continue to work.
  - Existing consumers that branch only on `status_reason="carryover_non_outdated_unresolved_thread"` for carryover-only missing-completion must switch to inventory fields or optional `actionable_inventory_reason`.
  - `review_completion_unknown` remains the same reason string, reducing downstream churn for unknown handling.
- Rollback:
  - Revert the classification split and tests if it causes downstream incompatibility.
  - Because the design avoids new top-level statuses, rollback is localized to `pr_observation_snapshot.py`, `pr_observation_wait.py`, docs, and tests.
- Migration risk:
  - The main semantic change is that some previously terminal carryover-only observations become non-terminal wait/resume until completion or guard satisfaction.

## 11. Observability

- Final stdout JSON remains authoritative.
- Progress stderr should remain bounded and non-authoritative.
- Recommended progress improvement:
  - Continue showing review lifecycle as pending/unknown when completion is missing.
  - Add or preserve a compact carryover count in progress if line budget allows, e.g. `carryover=8`.
- `--out` artifacts remain debug/audit copies only.
- `decision_fingerprint` must include any new `decision.actionable_inventory_reason` field if the field is inserted into `decision`.

## 12. Test Strategy

Regression cases:

- Guard-under carryover-only wait:
  - CI passed, head matched, current selected unresolved 0, carryover 1+, completion none, latency guard false.
  - Expect `pending` / `wait_or_resume` / `observation_complete=false` / `missing_current_completion_signal`; carryover IDs retained.
- Guard-satisfied carryover-only wait:
  - Same inventory, latency guard true.
  - Expect `human_gate` / `human_gate` / `review_completion_unknown` / `post_unknown_fresh_audit_required=true`; carryover IDs retained.
- Snapshot carryover-only missing-completion:
  - One-shot snapshot should align with non-terminal missing completion rather than terminal feedback handling.
- Current selected unresolved priority:
  - Current selected unresolved plus carryover returns `current_selected_unresolved_thread` and `address_review_feedback`.
- Trusted completion plus carryover:
  - Submitted current PR review completion plus carryover returns `carryover_non_outdated_unresolved_thread` and `address_review_feedback`.
- Fallback issue comment:
  - Remains low-confidence `wait_or_resume`/human gate path; no trusted completion promotion.
- CI/head blockers:
  - Failed/pending/running CI, stale head, draft/non-open PR, blocking limitations keep existing priority over review/carryover classification.
- Outdated or unavailable thread state:
  - Not promoted into actionable inventory.

Suggested checks after implementation:

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "issue_219 or issue_187_s420 or review_completion_unknown"
uv run pytest tests/unit/infra/test_init_update.py
```

## 13. ADR Candidates

- ADR not recommended for this issue.
- Reason:
  - The decision refines an existing PR observation contract and is captured by issue requirement/design/plan plus tests.
  - It is important and somewhat surprising, but not broad enough to warrant a new long-lived architecture decision if canonical issue docs and skill docs are updated.
- ADR candidate only if:
  - The project introduces a generalized status reason taxonomy across multiple skills, or
  - `fallback_issue_comment` / no-findings artifact policy is redesigned across PR observation workflows.

## 14. Risks

- Downstream consumer ambiguity:
  - Consumers may previously have used `status_reason` alone to find carryover work. Mitigate with counts/IDs and optional `actionable_inventory_reason`.
- Infinite or extended waits:
  - Carryover-only will no longer terminate before completion/guard. Mitigate through existing timeout/resume metadata and latency guard promotion.
- False no-work reporting:
  - If docs do not emphasize counts/IDs, agents may misread `review_completion_unknown` as no review work. Mitigate with skill docs and report guidance.
- Provider/mirror drift:
  - Editing `.agents/...` directly without provider-side source update would be lost. Mitigate by changing provider source first and then verifying dogfooding mirror.

## 15. Requirement Clarification Requests

- Blocking clarification: none.
- Non-blocking implementation choice:
  - Main orchestrator should decide whether `decision.actionable_inventory_reason` is mandatory in the final design or an optional helper. This draft recommends adding it because it preserves machine-readable carryover context without overloading `status_reason`.

## 16. Integration Notes for Main Orchestrator

- Adopt the two-axis model into canonical `design.md`:
  - current review lifecycle controls `status_reason`
  - carryover remains decision-facing actionable inventory
- Adopt the state classification table into canonical design or plan.
- Record evidence adoption in `report.md` for:
  - source analysis
  - incomplete-stop interview
  - policy synthesis
  - unknown reason naming interview
  - this draft
- Do not claim spec-reviewer approval from this draft.
- Do not treat this draft as implementation readiness. A fresh canonical design and fresh reviewer pass remain required.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
