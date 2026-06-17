---
created_by_role: system-architect
scope_id: iss-00187-actions-pr-observation-ci-state
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/epic/design.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/reference_sync.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t225521z-14-disc-missed-p2-reserve-next-observation-poll.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t225521z-15-disc-pr-observation-missed-review-root-cause.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t161435z-12-disc-pr-repair-batch-after-s399-observation.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t161435z-13-disc-pr-repair-unit-u001-ci-observation-p1.md
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# System Architect Draft: Review Inventory and Wait Budget Design Addendum

## 1. Requirement Coverage

This draft is an additive design proposal for `iss-00187`. It does not replace the current Actions-primary CI design. It integrates the newly discovered PR #190 P2 review and the review-observation classification gap into the existing contract.

Covered requirement surfaces:

- AC-001..AC-005 remain covered by the Actions-primary CI collector, supplemental limitation semantics, provider/mirror policy, and secret-safe JSON output.
- AC-006 and AC-007 remain the direct requirement anchors for `review_completion_unknown`, pending review preservation, and non-pass human-gate behavior.
- The new discovery does not change the accepted rule that `review_completion_unknown` is non-pass. It adds stronger preconditions and post-unknown obligations so "unknown" cannot be read as "no review work".
- The new discovery exposes a design gap adjacent to AC-006: current-boundary selected blockers are not enough to describe all actionable review work when all-fetched non-outdated unresolved threads exist.
- The new P2 wait-loop finding is a reliability addendum to AC-006 wait behavior: the wait loop must not sleep away the budget needed for a meaningful next observation poll.

Requirement impact:

- No new user-facing GitHub permission or public CLI option is required.
- No expansion to PR merge automation is required.
- Canonical `requirement.md` may need a narrow AC/edge-case amendment if the orchestrator wants `actionable_unresolved_count` to become a hard acceptance criterion rather than a design-level strengthening of AC-006.

## 2. Existing Context Findings

Existing `design.md` already establishes these relevant invariants:

- Provider source under `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` is authoritative; dogfooding `.agents/...` is a mirror / validation surface.
- stdout remains the single final JSON authority; progress and diagnostics stay on stderr.
- Public shell command names and arguments remain stable.
- No arbitrary endpoint, GraphQL query, raw `gh` argument, header, or request body is accepted from callers.
- Actions workflow runs/jobs are the primary CI observation surface; check runs, commit statuses, and PR rollup are supplemental.
- Supplemental permission denial must not become the normal blocker when Actions or strict external green evidence is decisive.
- `selected_unresolved_count == 0`, `selected_comments == 0`, and `completion_signal="none"` are not review completion.
- `review_completion_unknown` is a non-pass, terminal-like human gate, not `passed` and not `merge_prepared`.
- Current selected unresolved threads and current changes-requested evidence override no-completion unknown.
- Pending review request / pending current review signal remains pending and must not be promoted to `review_completion_unknown`.
- Zero Actions runs alone is not CI success, but strict readable external green evidence can pass if no failure/pending/required-missing blocker exists.

The newly read PR #190 discussions add four findings:

- The P2 review comment `3422572159` was posted after the `bb50b7a2` observation had already stopped, so that specific comment was a late-review race relative to that run.
- The wait loop can consume the remaining deadline in sleep and start a final snapshot with too little budget, allowing a less useful timeout snapshot to overwrite a meaningful latest payload.
- The latest observation contained `review.threads.unresolved=3` while selected current-boundary unresolved counts were zero, exposing a classification gap rather than a GitHub retrieval failure.
- The previous U001 CI repair fixed bounded job expansion and external-green / Checks-read limitation behavior, but it does not solve the review inventory gap or the P2 wait-loop budget race.

## 3. Design Decisions

Decision A: introduce first-class actionable review inventory.

- Keep the existing selected-current-boundary model.
- Add an inventory layer that separates current-selected unresolved threads from non-outdated carryover unresolved threads.
- Treat actionable review inventory as the merge-prepared / repair-batch gate, not as raw audit data.

Decision B: preserve `review_completion_unknown`, but narrow its meaning.

- It means "blind waiting may stop because trusted completion is still not observable after stability and latency guards."
- It does not mean "there is no review work."
- It can be emitted only when actionable unresolved review inventory is empty and no pending/blocking review collection state exists.

Decision C: decision precedence must evaluate review inventory before stable unknown.

Recommended precedence:

1. current-selected changes requested / unresolved thread
2. carryover non-outdated unresolved thread
3. blocking collection limitation
4. pending review request or pending current review signal
5. explicit trusted completion signal
6. stable no-completion evidence -> `review_completion_unknown`

Decision D: reserve budget for the next observation poll.

- Wait-loop sleep must preserve enough remaining time for another meaningful snapshot attempt.
- If remaining time is insufficient and a latest useful payload exists, the wait loop should stop from that latest payload with explicit wait metadata instead of launching an under-budget poll that can degrade the result.

Decision E: require post-unknown fresh audit before final merge-prepared reporting.

- `review_completion_unknown` is a human gate. After it appears, orchestration should run or consume a fresh review inventory audit before claiming no actionable review work.
- This is especially important when CI passed shortly before the stop condition or recent review activity is close to the observation window.

## 4. Alternatives Considered

Alternative 1: extend the wait latency thresholds only.

- Rejected as insufficient. Larger trigger / CI-passed age thresholds reduce one race but do not address all-fetched non-outdated unresolved threads being hidden below selected current-boundary fields.

Alternative 2: treat any all-fetched unresolved thread as blocking.

- Rejected as too broad. Outdated, stale, or unrelated historical threads must remain audit data unless they still apply to the latest head/diff.

Alternative 3: change `review_completion_unknown` into `pending`.

- Rejected. The current design intentionally avoids generic timeout/pending loops after stability and latency gates. The problem is not the existence of the human gate; the problem is missing actionable inventory and insufficient late-review audit.

Alternative 4: launch one more snapshot unconditionally at the deadline.

- Rejected. This repeats the P2 failure mode when there is not enough time for the snapshot to complete and may overwrite a better latest payload.

Alternative 5: make merge-preparer inspect raw `review.threads.unresolved` directly.

- Rejected as the primary contract. Raw audit fields are useful, but downstream orchestration needs a normalized actionable inventory with freshness / outdatedness classification and stable decision precedence.

## 5. Boundary / Contract Model

Existing boundary remains:

- `fetch_pr_review_snapshot.sh` / its Python extraction equivalent owns review collection and current-boundary review lifecycle normalization.
- `fetch_pr_observation_snapshot.sh` / `pr_observation_snapshot.py` owns combined CI/head/review snapshot classification.
- `wait_pr_observation.sh` / `pr_observation_wait.py` owns polling, quiet / same-fingerprint stability, review latency gates, timeout behavior, resume metadata, and final wait metadata.
- Merge-preparer / orchestrator owns final human decision, commit/push/PR mutation, and canonical report adoption.

Additive review inventory contract:

```json
{
  "review_threads": {
    "all_fetched": {
      "non_outdated_unresolved": []
    },
    "current_selected": {
      "unresolved": []
    },
    "carryover_non_outdated_unresolved": []
  },
  "decision": {
    "actionable_unresolved_count": 0,
    "current_selected_unresolved_count": 0,
    "carryover_unresolved_count": 0,
    "actionable_unresolved_thread_ids": [],
    "carryover_unresolved_thread_ids": []
  }
}
```

Compatibility aliases may be placed under existing `review.threads` / `codex_review.collection_summary` if implementation discovers a better local fit, but the decision-level actionable counts should be first-class.

Decision output semantics:

- If current-selected unresolved exists:
  - `summary.review="unresolved"`
  - `decision.status_reason="current_selected_unresolved_thread"`
  - `recommended_next_action="address_review_feedback"`
- If only carryover non-outdated unresolved exists:
  - `summary.review="unresolved"`
  - `decision.status_reason="carryover_non_outdated_unresolved_thread"`
  - `recommended_next_action="address_review_feedback"`
- If no actionable unresolved exists and no pending/blocking state exists, stable no-completion evidence may still become `review_completion_unknown`.
- `decision.selected_unresolved_count` remains for compatibility, but consumers must not treat it as the total actionable review count.

Wait-loop budget contract:

- Track recent successful snapshot elapsed time.
- Compute `wait.next_poll_min_budget_seconds` from a small floor plus recent elapsed time and slack.
- Before sleeping, reserve that budget.
- Before starting a new poll, skip under-budget polling when a latest useful payload exists.
- Add explicit metadata such as `wait.next_poll_budget_reserved`, `wait.last_snapshot_elapsed_seconds`, and `wait.final_poll_skipped_reason="insufficient_next_snapshot_budget"`.

## 6. Dependency Analysis

Upstream dependencies:

- `requirement.md` AC-006 / AC-007 define the non-pass review unknown and pending-review preservation boundary.
- Existing `design.md` S100/S101/S204/S300+ addenda define no-completion evidence, wait promotion, timing guards, and Python entrypoint extraction.
- The P2 wait-loop discussion targets `pr_observation_wait.py`, which is already the correct owner after S320 extraction.
- The missed-review root-cause discussion shows that review inventory classification must live before merge-preparer reporting, not only in human prose.

Downstream dependencies:

- `github-pr-merge-preparer` and the main orchestrator consume `normalized_status`, `recommended_next_action`, `summary.review`, and `decision.*`.
- Existing tests in `tests/unit/infra/test_init_update.py` are the likely fake-`gh` regression home.
- Provider/mirror sync must include any touched provider assets under `.agents/skills/github-pr-observation/`.

Dependency risks:

- If `review_threads` payload shape is hidden only in nested audit data, downstream consumers may keep using selected counts and miss carryover blockers.
- If wait-loop budget metadata is added only to timeout cases, normal human-gate payloads may still lack enough evidence to explain why observation stopped.
- If merge-preparer behavior is changed before PR observation output exposes actionable inventory, the downstream gate will have to parse raw thread data and duplicate classification logic.

## 7. Source of Record

Source-of-truth policy should remain unchanged:

- Provider implementation source:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - provider review collector script/module if inventory classification is implemented there
- Dogfooding mirror:
  - `.agents/skills/github-pr-observation/...`
  - mirror is validation / installed-surface inspection, not implementation authority.
- Canonical design and plan:
  - main orchestrator only.
  - this discussion is unreviewed evidence until adopted into canonical docs and passed by fresh `spec-reviewer`.
- Report evidence:
  - `report.md` should record whether this draft is adopted, partially adopted, superseded, or rejected.

## 8. Data Flow / Domain Model / Interface Contract

Review data flow:

```text
GitHub PR reviews/comments/threads
  -> review collector
  -> raw audit thread data
  -> current-selected classifier
  -> non-outdated carryover classifier
  -> actionable review inventory
  -> snapshot decision
  -> wait decision / merge-preparer gate
```

State model:

- `current_selected_unresolved`: feedback selected by current trigger/review boundary.
- `carryover_non_outdated_unresolved`: unresolved review feedback not selected by the current boundary but still applicable to the latest head/diff.
- `all_fetched_unresolved`: audit set; not automatically actionable until classified as non-outdated and relevant.
- `actionable_unresolved`: union of current-selected unresolved and carryover non-outdated unresolved.
- `review_completion_unknown`: non-pass human gate that requires actionable inventory to be empty and completion evidence to remain absent after stability / latency / budget guards.

Interface additions should be additive:

- Add `decision.actionable_unresolved_count`.
- Add `decision.actionable_unresolved_thread_ids`.
- Add `decision.current_selected_unresolved_count`.
- Add `decision.carryover_unresolved_count`.
- Add `decision.carryover_unresolved_thread_ids`.
- Add a structured `review_threads` or `codex_review.review_threads` inventory object.
- Add wait budget metadata under `wait.*`.
- Add `latest_review_activity_at` and `latest_review_activity_age_seconds` when reliably available.

Do not remove:

- `decision.selected_unresolved_count`
- `decision.selected_review_thread_ids`
- existing `review.threads.*` audit fields
- existing `summary.review`
- existing `review_completion_unknown` reason/action shape

## 9. File / Module Change Plan

Expected canonical design additions should target these sections:

- `既存実装 / 規約の理解`
  - Add the PR #190 missed-review facts and the distinction between late review race and classification gap.
- `採用方針 / トレードオフ`
  - Add actionable review inventory, decision precedence, and wait-loop next-poll budget guard decisions.
- `インターフェース契約`
  - Add additive JSON fields and compatibility policy.
- `シーケンス差分`
  - Add inventory classification before `review_completion_unknown` promotion and under-budget poll skip behavior.
- `ドメインモデル差分`
  - Define current-selected, carryover non-outdated, all-fetched audit, and actionable unresolved review inventory.
- `ディレクトリ / ファイル変更計画`
  - Add provider review/wait modules, mirror files, and focused tests.
- `テスト戦略`
  - Add tests for selected-empty/carryover-present, outdated-only audit data, precedence, post-unknown fresh audit metadata, and insufficient next-poll budget.
- `リスク / 移行 / ロールバック`
  - Add late review race, stale carryover classification, and budget-guard regression risks.

Likely implementation touchpoints if adopted:

- Provider review collector or snapshot module for actionable inventory construction.
- Provider wait module for next-poll budget reservation and post-unknown metadata.
- Provider / mirror docs if operator semantics change.
- Fake `gh` tests in `tests/unit/infra/test_init_update.py`.

## 10. Migration / Compatibility / Rollback

Compatibility:

- JSON changes must be additive.
- Existing consumers of `selected_unresolved_count` continue to work, but should be guided toward `actionable_unresolved_count` for merge-prepared and repair-batch decisions.
- `summary.review` can change from `none` to `unresolved` when carryover non-outdated unresolved feedback exists. This is an intentional safety tightening, not an incompatible field removal.
- Wait budget metadata is additive under `wait`.

Migration:

- Update provider first.
- Sync dogfooding mirror after provider behavior stabilizes.
- Update tests before relying on live PR #190 observation.
- If canonical `plan.md` is updated, add one repair step for inventory classification and one repair step for wait-loop budget guard unless the orchestrator intentionally combines them under a single small repair unit.

Rollback:

- Reverting provider scripts/modules and tests restores prior behavior because public CLI surface remains stable.
- If inventory classification produces false positives, rollback should remove only the carryover promotion path while keeping current-selected behavior.
- If wait budget guard causes premature stop, rollback should disable under-budget poll skipping while retaining latest payload preservation tests as evidence for a narrower fix.

## 11. Observability

The final JSON should make these states obvious without reading raw review payloads:

- CI/head state.
- Trusted completion signal or lack of it.
- Current-selected unresolved count and IDs.
- Carryover non-outdated unresolved count and IDs.
- Total actionable unresolved count and IDs.
- Latest review activity time / age when known.
- Whether `review_completion_unknown` was blocked by actionable inventory, pending review, blocking collection failure, or latency/budget guard.
- Whether the final poll was skipped because remaining time was insufficient for a meaningful snapshot.

Suggested wait metadata:

- `wait.next_poll_min_budget_seconds`
- `wait.next_poll_budget_reserved`
- `wait.last_snapshot_elapsed_seconds`
- `wait.final_poll_skipped_reason`
- `wait.latest_review_activity_at`
- `wait.latest_review_activity_age_seconds`
- `wait.post_unknown_fresh_audit_required`

Operator-facing summary:

- If `decision.actionable_unresolved_count > 0`, `summary.review` should be `unresolved`.
- If `review_completion_unknown` appears with zero actionable inventory, summary should still communicate human gate, not no-review success.

## 12. Test Strategy

Add fake-`gh` regression tests for:

- Current-selected unresolved thread exists:
  - expected `decision.actionable_unresolved_count > 0`
  - reason `current_selected_unresolved_thread`
  - action `address_review_feedback`
- Selected IDs are empty but all-fetched non-outdated unresolved thread exists:
  - expected carryover count > 0
  - `summary.review="unresolved"`
  - no `review_completion_unknown`
- All fetched unresolved threads are outdated only:
  - expected audit data remains visible
  - actionable count is 0
  - no address-review action solely from outdated data
- Both current-selected and carryover unresolved exist:
  - current-selected reason wins
  - carryover IDs remain listed
- Stable no-completion with no actionable inventory:
  - `review_completion_unknown` remains possible after existing latency/stability guards.
- Late review activity before stop:
  - recent activity resets or blocks unknown promotion until quiet relative to review activity is satisfied.
- Wait loop insufficient next-poll budget:
  - latest useful payload is preserved
  - final under-budget snapshot is skipped
  - metadata records `insufficient_next_snapshot_budget`
- Sleep budget preservation:
  - loop sleep leaves enough time for the next snapshot based on floor + observed snapshot elapsed + slack.

Keep existing tests for:

- Actions-primary CI pass/fail/running/pending.
- external-green fallback and permission limitation behavior.
- head freshness / stale head.
- pending review signal not promoted to unknown.
- `review_completion_unknown` non-pass human gate.

## 13. ADR Candidates

No new ADR is required if this remains issue-local PR observation behavior.

ADR candidate only if one of these becomes cross-cutting:

- A repo-wide contract that every agent-facing PR observation consumer must use actionable review inventory instead of selected current-boundary fields.
- A durable policy for late AI-review publication windows across multiple skills or plugins.
- A generalized "latest useful payload must not be overwritten by under-budget polling" rule across other wait wrappers.

## 14. Risks

- Carryover classification may mark stale or outdated historical feedback as actionable if outdatedness or latest-head relevance is inferred too loosely.
- A too-strict carryover rule may keep PRs human-gated even after feedback has been made obsolete by new commits.
- A too-lenient carryover rule repeats the current missed-review risk.
- Larger or configurable latency gates can slow merge-preparer feedback loops without proving review completion.
- Post-unknown fresh audit can become duplicated polling if ownership between wait wrapper and merge-preparer is not explicit.
- Budget reservation may stop before one last useful poll if the floor/slack is too conservative.
- Existing downstream exact-payload consumers may ignore new actionable fields and continue relying on `selected_unresolved_count`.

Mitigations:

- Keep raw audit fields and normalized actionable fields side by side.
- Add negative tests for outdated-only unresolved threads.
- Keep `review_completion_unknown` non-pass.
- Require `summary.review` / `recommended_next_action` to reflect actionable inventory.
- Do not change public CLI surface.
- Record budget-guard metadata in the same final JSON.

## 15. Requirement Clarification Requests

No blocking clarification is required for a design addendum draft.

Non-blocking questions for the main orchestrator:

- Should `actionable_unresolved_count == 0` become an explicit acceptance criterion in `requirement.md`, or remain a design-level strengthening of AC-006?
- Should post-unknown fresh audit be owned by `wait_pr_observation.sh` before returning, or by `github-pr-merge-preparer` after receiving a human-gate payload?
- What default latency should replace or augment the existing `review_completion_unknown_min_ci_passed_age_seconds=90`, given PR #190 showed a later review after that threshold?
- What exact source field should define "non-outdated" for review threads in fake `gh` fixtures and live GitHub payloads?

## 16. Integration Notes for Main Orchestrator

Recommended canonical `design.md` chapter additions:

1. Add a subsection under `採用方針 / トレードオフ`: `Actionable review inventory and carryover non-outdated unresolved threads`.
2. Add a subsection under `インターフェース契約`: `Review inventory output JSON`.
3. Add a subsection under `シーケンス差分`: `Review inventory before review_completion_unknown promotion`.
4. Add a subsection under `シーケンス差分` or `Wait wrapper contract`: `Next observation poll budget guard`.
5. Add a subsection under `リスク / 移行 / ロールバック`: `Late review race and carryover classification risk`.
6. Add tests to `テスト戦略` for selected-empty/carryover-present, outdated-only, precedence, post-unknown audit, and insufficient next-poll budget.

Suggested plan impact:

- Add a repair step for review inventory classification and decision precedence.
- Add a repair step for wait-loop next-poll budget reservation.
- Add a final live PR #190 re-observation gate that reports `decision.actionable_unresolved_count`, current-selected IDs, carryover IDs, latest review activity, CI/head state, and whether P2 `3422572159` remains unresolved/non-outdated.

Adoption notes:

- This draft is intentionally additive. It does not invalidate S01-S320 work.
- The current design's `review_completion_unknown` remains useful but must be constrained so it cannot hide actionable unresolved review inventory.
- `summary.review` should be aligned with actionable inventory, not only current-selected completion evidence.
- The main orchestrator must decide whether to first amend `requirement.md` or adopt this directly into `design.md` as a conservative safety refinement.

## Handoff

- Changed discussion artifact path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t231000z-16-disc-system-architect-review-inventory-and-wait-budget-design-draft.md`
- Source requirement revision: `iss-00187` `requirement.md`, frontmatter `最終更新: "2026-06-16"`, active issue context `init-local-00003 / epic-00158 / iss-00187`
- Lightweight provenance summary: read active context, active issue requirement/design/plan/report, parent initiative/epic designs, spec authoring/design workflow docs, reference sync, and the four requested PR #190 / U001 discussion inputs.
- Leaf evidence used: none.
- Forbidden actions avoided: no canonical edit, no implementation edit, no test/config/GitHub mutation, no phase promotion, no reviewer-pass claim, no user-dialogue ownership.
- Unresolved requirement gaps: none blocking; non-blocking clarification candidates are listed in section 15.
- No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.

review_status: draft-ready
