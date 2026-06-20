---
種別: draft-plan
ID: "20260620t025710z-draft-plan-carryover-observation-implementation-plan"
タイトル: "Issue219 Carryover Observation Implementation Plan Draft"
status: proposed
created_by_role: implementation-planner
scope_id: iss-00219
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - .agents/skills/github-pr-observation/SKILL.md
  - .agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py
  - .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
  - .agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Issue219 Carryover Observation Implementation Plan Draft

This is delegated planning evidence only. It is not canonical `plan.md`, not reviewer approval, and not implementation readiness.

## 1. Plan Summary

Issue219 should be implemented as a narrow classification correction for `github-pr-observation`: keep carryover unresolved threads as decision-facing actionable inventory, but stop treating carryover-only missing-current-completion as immediate terminal feedback before the current `@codex review` lifecycle reaches either trusted completion or latency-guarded unknown.

The execution order should be:

1. S01 regression tests: lock the Issue219 matrix and update/supersede the existing Issue187 expectation where carryover-only snapshot previously blocked unknown.
2. S02 provider runtime classification fix: split current selected feedback from carryover inventory in snapshot and wait classification.
3. S03 skill docs and mirror resolution: update operator-facing two-axis semantics and confirm provider/mirror handling.
4. S90 docs impact: record canonical plan/report/docs impact without mixing it into runtime/test commits.
5. S99 final quality gate: run focused and issue-wide verification plus QA/code/spec reviews before closeout.

One step equals one behavior slice, one review scope, and one commit boundary. A no-op step still needs report evidence and an approved no-op gate.

## 2. Requirement / Design Traceability

- Requirement source: `spec-dock/active/issue/requirement.md`, ID `iss-00219`, last updated `2026-06-20`.
- Design source: `spec-dock/active/issue/design.md`, ID `iss-00219`, last updated `2026-06-20`.
- Report source: `spec-dock/active/issue/report.md`, plan phase pending, design review passed per report ledger.
- Implementation source of truth per design: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/...`.
- Dogfooding mirror evidence source: `.agents/skills/github-pr-observation/...`.

Trace summary:

- AC-001, AC-003, AC-005 drive the core wait/snapshot classification split.
- AC-002, AC-004 preserve immediate feedback handling for current selected blockers and trusted-completion-plus-carryover.
- AC-006 drives skill documentation and future-agent interpretation.
- EC-001 prevents fallback issue comment policy drift into Issue219.
- EC-002 keeps outdated or unknown-outdated threads out of actionable inventory.
- EC-003 preserves CI/head priority over review policy.
- EC-004 preserves existing empty-inventory `review_completion_unknown`.

## 3. Milestones

- M1 regression lock: S01 creates or updates tests so the current carryover-only premature stop fails before runtime changes.
- M2 runtime correction: S02 changes provider-side classification while preserving collector inventory split.
- M3 operator contract: S03 updates skill guidance and resolves provider/dogfooding mirror expectations.
- M4 documentation ledger: S90 records docs impact, adoption notes, closure deltas, and no-op/changed evidence.
- M5 final gate: S99 confirms AC/EC closure with QA, code review, spec review, and final verification.

## 4. Dependency-Derived Execution Order

Design dependency analysis shows `pr_review_snapshot.py` collects inventory first, `pr_observation_snapshot.py` and `pr_observation_wait.py` classify it, and `SKILL.md` explains the contract. Therefore tests should lock behavior before code, runtime classification should change before docs/mirror wording, and final gates should run after report evidence exists.

Execution queue:

| Step | Depends on | Unblocks | Target behavior |
|---|---|---|---|
| S01 | approved requirement/design evidence | S02 | failing regression matrix for carryover-only lifecycle/inventory split |
| S02 | S01 red/characterization evidence | S03, S90 | provider runtime returns wait/unknown/current-feedback/trusted-carryover correctly |
| S03 | S02 runtime behavior | S90 | skill docs and mirror evidence explain the two-axis contract |
| S90 | S01-S03 step evidence | S99 | canonical docs/report impact is recorded without changing runtime behavior |
| S99 | S01-S90 | final closeout readiness review | issue-wide verification and reviewer gates |

## 5. Issue / Step Slicing

### S01 Regression Tests - Carryover-only no longer blocks current lifecycle observation

- Behavior goal: lock Issue219's observable matrix in `tests/unit/infra/test_init_update.py`, including the existing Issue187 expectation that carryover-only snapshot previously blocked unknown and now must be updated or superseded.
- Target files:
  - `tests/unit/infra/test_init_update.py`
- Verification commands:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_219 or issue_187_s420 or issue_187_s430"`
- Reviewer focus:
  - `code-reviewer`; focus on test sensitivity, fixture realism, and whether the failing path proves public script JSON behavior rather than private helper internals.
- Commit/no-op gate:
  - Commit if tests are changed and reviewed.
  - No-op is allowed only if an existing test already fails for every required Issue219 row; record exact failing tests in `report.md`.

Delegation contract:

- delegated role: `dev-coder`
- input docs: requirement, design, this plan, `phase_plan_issue.md`, `authoring/issue-plan.md`, target test areas around Issue187 S410/S420/S430.
- allowed paths: `tests/unit/infra/test_init_update.py`
- forbidden changes: runtime code, skill docs, canonical docs, GitHub state, unrelated tests.
- acceptance criteria: AC-001..AC-005 and EC-001..EC-004 have red or characterization coverage seeds.
- required tests: add/adjust public wrapper-level tests using existing fake snapshot/fake gh patterns.
- stop conditions: if existing fixture helpers cannot express latency/carryover without runtime edits, stop and request plan amendment or a dedicated test helper step.
- output required: changed test list, expected pre-fix failures, command output, and note on superseding Issue187 expectation.

#### 具体テストケース一覧

- `tc-s01-001` acceptance: guard-under carryover-only wait remains wait/resume
  - 前提: CI passed, head matched, current selected unresolved 0, completion signal none, carryover unresolved count 1, latency guard not satisfied.
  - 操作: wait script fixture classification is executed through existing fake snapshot helper.
  - 期待結果: `recommended_next_action="wait_or_resume"`, `observation_complete=false`, `decision.status_reason="missing_current_completion_signal"`, carryover ids remain present.
  - 失敗検出: carryover-only inventory causes `address_review_feedback` before trusted completion or latency guard.
  - 検証方法: `tests/unit/infra/test_init_update.py` Issue219 wait regression.
  - 関連 closure id: AC-001, AC-005

- `tc-s01-002` regression: Issue187 carryover-only snapshot expectation is updated or superseded
  - 前提: Existing `test_issue_187_s420_snapshot_carryover_unresolved_blocks_unknown` currently expects `carryover_non_outdated_unresolved_thread`.
  - 操作: revise or supersede it with Issue219 naming that preserves carryover inventory but no longer treats missing completion as current feedback.
  - 期待結果: guard-under snapshot returns the missing-completion wait family, while trusted completion plus carryover still returns carryover feedback.
  - 失敗検出: the old Issue187 expectation masks Issue219 by continuing to require terminal carryover feedback for missing-completion.
  - 検証方法: focused pytest on Issue187 S420 and Issue219 tests.
  - 関連 closure id: AC-001, AC-004, AC-005

- `tc-s01-003` acceptance: current selected unresolved still wins immediately
  - 前提: CI passed, current selected unresolved thread exists, carryover may also exist.
  - 操作: snapshot and wait fixtures classify the payload.
  - 期待結果: `human_gate` / `address_review_feedback`, reason `current_selected_unresolved_thread`.
  - 失敗検出: the new carryover split accidentally delays current selected feedback.
  - 検証方法: focused pytest with existing `current_selected_reason_wins_over_carryover` pattern.
  - 関連 closure id: AC-002, AC-005

- `tc-s01-004` acceptance: latency-satisfied carryover-only becomes review completion unknown
  - 前提: AC-001 state, but trigger age and CI-passed age satisfy unknown latency guards.
  - 操作: wait fake snapshots with resume/age metadata.
  - 期待結果: top-level `human_gate`, `decision.status="unknown"`, `decision.status_reason="review_completion_unknown"`, `wait.post_unknown_fresh_audit_required=true`, carryover ids remain present.
  - 失敗検出: carryover inventory prevents unknown forever or is dropped from the final JSON.
  - 検証方法: focused pytest on wait latency path.
  - 関連 closure id: AC-003, AC-005

- `tc-s01-005` acceptance: trusted completion plus carryover remains feedback handling
  - 前提: trusted submitted PR review completion signal exists, no current selected unresolved, carryover unresolved count 1.
  - 操作: snapshot and wait fixtures classify the payload.
  - 期待結果: `human_gate` / `address_review_feedback`, reason `carryover_non_outdated_unresolved_thread`, carryover ids retained.
  - 失敗検出: the split incorrectly treats trusted completion plus carryover as pass or unknown.
  - 検証方法: focused pytest.
  - 関連 closure id: AC-004, AC-005

- `tc-s01-006` edge: fallback issue comment policy is unchanged
  - 前提: completion signal `fallback_issue_comment` with or without carryover inventory.
  - 操作: snapshot/wait fixture classification.
  - 期待結果: existing fallback low-confidence path remains non-promoting and is not treated as trusted completion.
  - 失敗検出: Issue219 accidentally resolves Issue218 policy or promotes fallback.
  - 検証方法: focused pytest around existing fallback tests.
  - 関連 closure id: EC-001

Step closure contract:

- All new/updated tests fail against the pre-fix runtime or are explicitly marked as characterization if already failing.
- Closure rows AC-001..AC-005 and EC-001..EC-004 have at least one concrete test seed.
- Report records the Issue187 expectation update/supersession.

### S02 Provider Runtime Classification Fix - split current selected feedback from carryover inventory

- Behavior goal: update provider-side runtime classification so current review lifecycle controls wait/unknown and carryover inventory remains visible without premature terminal stop.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` only if needed for optional `decision.actionable_inventory_reason` or fingerprint support.
- Verification commands:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_219 or issue_187_s420 or issue_187_s430 or fallback_issue_comment"`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation"`
- Reviewer focus:
  - `code-reviewer`; focus on public JSON compatibility, reason taxonomy, latency guard behavior, and avoiding fallback Issue218 changes.
- Commit/no-op gate:
  - Commit after S01 tests pass and reviewer passes.
  - No-op only if provider runtime already satisfies all Issue219 tests without changes; record exact evidence.

Delegation contract:

- delegated role: `dev-coder`
- input docs: requirement, design, this plan, S01 test evidence, provider runtime files.
- allowed paths: provider-side runtime files listed above.
- forbidden changes: `.agents` mirror direct edits, skill docs, tests beyond S01, GitHub API collection redesign, authentication policy, fallback issue comment promotion.
- acceptance criteria: AC-001..AC-005, EC-001..EC-004 pass through public wrapper-level tests.
- required tests: S01 focused test suite must pass; broaden to relevant PR observation tests if helper behavior changes.
- stop conditions: if solving requires changing GitHub collection scope, no-findings artifact contract, or new top-level status taxonomy, stop for plan amendment.
- output required: changed runtime files, reason split summary, verification output, unresolved risks, ledger note.

#### 具体テストケース一覧

- `tc-s02-001` implementation: snapshot classifies guard-under carryover-only as missing completion
  - 前提: S01 snapshot regression exists and fails pre-fix.
  - 操作: change snapshot helper usage so current selected blocker and carryover inventory are separate.
  - 期待結果: missing-current-completion snapshot no longer becomes `address_review_feedback` only because carryover exists.
  - 失敗検出: `actionable_unresolved_reason(...)` still treats carryover-only as terminal in snapshot.
  - 検証方法: S01 focused pytest.
  - 関連 closure id: AC-001, AC-005

- `tc-s02-002` implementation: wait unknown candidate allows carryover-only inventory
  - 前提: S01 latency-satisfied carryover-only wait regression exists.
  - 操作: update wait unknown candidate and finalization so carryover-only does not block `review_completion_unknown`.
  - 期待結果: latency guard controls unknown promotion, while carryover ids/counts remain in `decision`.
  - 失敗検出: `is_review_completion_unknown_candidate(...)` returns false for carryover-only.
  - 検証方法: S01 focused pytest.
  - 関連 closure id: AC-003, AC-005

- `tc-s02-003` implementation: current selected blocker priority remains terminal
  - 前提: current selected unresolved or selected changes requested exists.
  - 操作: run focused current selected tests.
  - 期待結果: current selected reason wins over carryover and returns feedback handling.
  - 失敗検出: current feedback is delayed into wait/unknown path.
  - 検証方法: S01 focused pytest plus existing Issue187 tests.
  - 関連 closure id: AC-002

- `tc-s02-004` implementation: trusted completion plus carryover remains terminal feedback
  - 前提: completion signal is `submitted_pull_request_review`, current selected blocker absent, carryover count positive.
  - 操作: run snapshot/wait classification fixtures.
  - 期待結果: `carryover_non_outdated_unresolved_thread` is used only after trusted completion for carryover-only feedback.
  - 失敗検出: trusted completion plus carryover is marked pass or unknown.
  - 検証方法: S01 focused pytest.
  - 関連 closure id: AC-004

- `tc-s02-005` edge: CI/head/fallback/outdated precedence remains unchanged
  - 前提: CI/head blocker, fallback issue comment, outdated/unavailable threads, and empty inventory unknown fixtures.
  - 操作: run existing targeted regression subset.
  - 期待結果: existing EC behavior remains stable.
  - 失敗検出: carryover split changes unrelated blockers or promotes outdated/fallback signals.
  - 検証方法: focused pytest on `fallback_issue_comment`, `outdated`, `unknown_outdated`, `stale_head`, `review_completion_unknown`.
  - 関連 closure id: EC-001, EC-002, EC-003, EC-004

Step closure contract:

- S01 tests pass without weakening AC/EC expectations.
- No new operator CLI mode, GitHub endpoint, or status taxonomy is introduced unless plan is amended.
- Runtime change remains provider-side first; mirror handling is deferred to S03.

### S03 Skill Docs and Mirror Resolution - explain and align the two-axis contract

- Behavior goal: update skill guidance so future agents read `review_completion_unknown`, `selected_unresolved_count == 0`, and carryover inventory as two separate axes; resolve provider/dogfooding mirror evidence.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md` only through the repo's accepted provider-to-mirror update/sync path or as an explicitly reviewed mirror update.
  - `.agents/skills/github-pr-observation/scripts/lib/*.py` mirror files only if S02 provider assets are intentionally synchronized into dogfooding mirror during this issue.
- Verification commands:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "github-pr-observation or pr_observation"`
  - `git diff -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation`
- Reviewer focus:
  - `spec-reviewer` for docs/spec alignment, plus `code-reviewer` if mirror runtime files are changed.
- Commit/no-op gate:
  - Prefer a separate docs/mirror commit after S02.
  - No-op allowed if provider docs already describe Issue219 semantics and mirror intentionally remains unsynced; report must explain why.

Delegation contract:

- delegated role: `doc-writer` for skill docs; `dev-coder` only if mirror runtime synchronization changes code assets.
- input docs: requirement, design, this plan, S02 runtime diff, current `SKILL.md`.
- allowed paths: listed skill docs/mirror files only.
- forbidden changes: runtime provider classification unless routed back to S02, canonical docs except report evidence, unrelated skills, `.codex`, `.github`, GitHub state.
- acceptance criteria: AC-006 and docs portions of AC-001/AC-003/AC-004 are readable from skill docs.
- required verification: docs diff inspection and focused scaffold/asset tests if provider assets are shipped.
- stop conditions: if mirror update requires broad scaffold regeneration or unrelated snapshot churn, stop for orchestrator decision.
- output required: docs diff summary, provider/mirror decision, verification result, ledger note.

#### 具体テストケース一覧

- `tc-s03-001` docs: `review_completion_unknown` no longer implies empty actionable inventory
  - 前提: Skill docs currently say unknown means actionable inventory was empty.
  - 操作: update wording to "no current-boundary selected actionable feedback" while carryover inventory may still be present.
  - 期待結果: future agents can see unknown is human gate and not no-review-work proof.
  - 失敗検出: docs still tell agents to treat all actionable inventory as empty.
  - 検証方法: docs diff inspection and spec review.
  - 関連 closure id: AC-006, AC-003

- `tc-s03-002` docs: carryover-only below latency guard remains wait/resume
  - 前提: Carryover inventory exists but current completion signal is missing below guard.
  - 操作: inspect updated `SKILL.md`.
  - 期待結果: docs say carryover does not replace current completion signal and should not trigger early terminal feedback.
  - 失敗検出: docs still instruct `address_review_feedback` for carryover-only missing-completion below guard.
  - 検証方法: docs diff inspection and spec review.
  - 関連 closure id: AC-001, AC-006

- `tc-s03-003` docs: trusted completion plus carryover remains actionable feedback
  - 前提: Trusted current completion exists and carryover unresolved remains.
  - 操作: inspect updated `SKILL.md`.
  - 期待結果: docs preserve `carryover_non_outdated_unresolved_thread` as feedback-handling after trusted completion.
  - 失敗検出: docs demote carryover to audit-only or pass.
  - 検証方法: docs diff inspection.
  - 関連 closure id: AC-004, AC-006

- `tc-s03-004` mirror: provider and dogfooding guidance are intentionally aligned or intentionally recorded as pending sync
  - 前提: Provider-side assets are source of truth; `.agents` is dogfooding mirror.
  - 操作: run diff/asset-focused checks after docs/mirror decision.
  - 期待結果: mirror status is not ambiguous in report evidence.
  - 失敗検出: provider docs and mirror docs diverge silently.
  - 検証方法: `git diff -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation`.
  - 関連 closure id: AC-006

Step closure contract:

- Skill docs explain lifecycle/inventory split, `selected_unresolved_count == 0`, unknown human gate, and carryover handling.
- Provider/mirror decision is explicit in `report.md`.
- Docs-only changes are reviewed separately from runtime/test changes unless mirror runtime files are synchronized.

### S90 Docs Impact - canonical ledger and release-facing documentation decision

- Behavior goal: resolve issue-local docs impact and record adopted evidence, closure deltas, and any no-op decisions without changing runtime behavior.
- Target files:
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/issue/plan.md` only by main orchestrator if this draft is adopted.
  - Additional docs only if S03/S90 finds shipped docs outside `SKILL.md` must change.
- Verification commands:
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- Reviewer focus:
  - `spec-reviewer`; focus on traceability, evidence adoption, closure delta, and whether docs impact is complete.
- Commit/no-op gate:
  - Separate docs/report commit or approved no-op evidence.
  - This delegated draft must not be treated as canonical adoption evidence until the main orchestrator records adoption.

Delegation contract:

- delegated role: main orchestrator for canonical docs/report; `doc-writer` only for additional shipped docs if needed.
- input docs: accepted requirement/design/plan, S01-S03 report evidence, this draft if adopted.
- allowed paths: canonical issue docs and explicitly identified shipped docs only.
- forbidden changes: runtime/test files, unrelated issue docs, existing discussion drafts, phase promotion.
- acceptance criteria: report contains step closure evidence, reviewer statuses, commit/no-op evidence, and any plan amendment history.
- required verification: `spec-dock validate` and diff guard.
- stop conditions: if canonical requirement/design changes are needed, stop for plan amendment and re-review.
- output required: docs impact table, evidence adoption ledger entries, unresolved risks.

#### 具体テストケース一覧

- `tc-s90-001` docs-impact: report ledger records Issue187 supersession
  - 前提: S01 updated or superseded an Issue187 test expectation.
  - 操作: inspect report ledger after S01-S02.
  - 期待結果: report explains why Issue187's carryover-only blocks-unknown expectation was replaced by Issue219.
  - 失敗検出: future reviewers cannot tell whether the test change was intentional.
  - 検証方法: report inspection and spec review.
  - 関連 closure id: AC-001, AC-005

- `tc-s90-002` docs-impact: report records provider/mirror resolution
  - 前提: S03 made a provider/mirror decision.
  - 操作: inspect report docs impact and delegated evidence sections.
  - 期待結果: provider source-of-truth and dogfooding mirror state are explicit.
  - 失敗検出: mirror drift is left ambiguous.
  - 検証方法: report inspection plus `git diff --check`.
  - 関連 closure id: AC-006

Step closure contract:

- Report contains observed evidence for every completed step.
- Any discovered closure delta has an amendment decision.
- No implementation-readiness or reviewer-pass is claimed by this draft.

### S99 Final Quality Gate - issue-wide closure and review

- Behavior goal: confirm all AC/EC rows are closed by evidence, tests, docs, and reviews before issue finish.
- Target files:
  - `spec-dock/active/issue/report.md`
  - final verification outputs only; no runtime/doc edits unless a reviewer finding creates a new step or plan amendment.
- Verification commands:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_219 or issue_187_s420 or issue_187_s430 or github-pr-observation or pr_observation"`
  - `uv run pytest tests/unit`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- Reviewer focus:
  - `qa-reviewer` for test sufficiency and missing high-value cases.
  - issue-wide `code-reviewer` for integrated runtime/test/doc diff.
  - `spec-reviewer` for requirement/design/plan/report alignment.
- Commit/no-op gate:
  - Final report update and final quality evidence may be a final docs commit if changed.
  - If no final changes are needed, record approved no-op and reviewer results.

Delegation contract:

- delegated role: `qa-reviewer`, issue-wide `code-reviewer`, `spec-reviewer`; main orchestrator coordinates.
- input docs: canonical requirement/design/plan/report, all step commits, verification outputs.
- allowed paths: report updates and reviewer-driven fixes routed to a new step/amendment.
- forbidden changes: silent runtime/test fixes during final gate, phase promotion without reviewer pass, GitHub state mutation.
- acceptance criteria: every closure index row has evidence, no unresolved P1/P2 reviewer findings, final verification commands recorded.
- required verification: commands listed above or documented equivalent if environment blocks them.
- stop conditions: any reviewer fail, failed verification caused by this change, missing closure evidence, or unplanned contract change.
- output required: final QA/code/spec reviewer results, final verification output, exit contract status.

#### 具体テストケース一覧

- `tc-s99-001` final-gate: AC/EC coverage audit
  - 前提: S01-S90 evidence exists.
  - 操作: qa-reviewer checks closure index rows against tests/docs/report evidence.
  - 期待結果: no required AC/EC row lacks evidence.
  - 失敗検出: a requirement is only asserted in prose without verification.
  - 検証方法: qa-reviewer result in report.
  - 関連 closure id: AC-001..AC-006, EC-001..EC-004

- `tc-s99-002` final-gate: integrated runtime and docs review
  - 前提: runtime, tests, skill docs, and report are updated.
  - 操作: code-reviewer and spec-reviewer review the integrated diff.
  - 期待結果: no open findings; docs and runtime contract agree.
  - 失敗検出: runtime JSON behavior and skill instructions diverge.
  - 検証方法: reviewer results in report.
  - 関連 closure id: AC-005, AC-006

Step closure contract:

- All final commands pass or failures are documented as unrelated with evidence.
- QA, code, and spec review gates pass.
- Final exit contract is satisfied before issue finish.

## 6. Test Strategy Mapping

Spec-Locked Closure Index:

| ID | Step | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|
| AC-001 | S01/S02 | acceptance | requirement AC-001 | Guard-under carryover-only missing completion stays non-terminal wait/resume with `missing_current_completion_signal` | CI passed, head matched, no current selected unresolved, completion none, carryover > 0, latency false | premature terminal feedback from carryover-only inventory | yes | red-required | S01/S02 report step closure |
| AC-002 | S01/S02 | acceptance | requirement AC-002 | Current selected unresolved or changes requested remains immediate feedback handling | current selected unresolved thread or selected changes requested exists | delayed current feedback | yes | red-required | S01/S02 report step closure |
| AC-003 | S01/S02 | acceptance | requirement AC-003 | Guard-satisfied carryover-only missing completion becomes `review_completion_unknown` human gate with fresh audit metadata | AC-001 state plus latency true | infinite wait or false carryover feedback | yes | red-required | S01/S02 report step closure |
| AC-004 | S01/S02 | acceptance | requirement AC-004 | Trusted completion plus carryover returns `address_review_feedback` with `carryover_non_outdated_unresolved_thread` | submitted PR review completion and carryover > 0 | false pass / false unknown after trusted completion | yes | red-required | S01/S02 report step closure |
| AC-005 | S01/S02/S99 | acceptance | requirement AC-005 | Snapshot and wait return the same next-action family and reason meaning for AC-001..AC-004 | one-shot and wait fixtures for each state | snapshot/wait contract divergence | yes | red-required | S01/S02/S99 report step closure |
| AC-006 | S03/S90/S99 | docs | requirement AC-006 | Skill docs explain lifecycle vs inventory, unknown semantics, selected count meaning, and carryover handling | updated `SKILL.md` and mirror decision | future-agent misread of JSON contract | yes | inspect-only | S03/S90/S99 report closure |
| EC-001 | S01/S02 | edge | requirement EC-001 | Fallback issue comment remains low-confidence and is not promoted to trusted completion | completion signal `fallback_issue_comment` | accidental Issue218 policy change | yes | covered-existing plus targeted regression | S01/S02 report closure |
| EC-002 | S01/S02 | edge | requirement EC-002 | Outdated or unknown-outdated unresolved threads remain audit/limitation context, not actionable inventory | thread `isOutdated=true` or null/unavailable | unsafe stale feedback promotion | yes | covered-existing | S01/S02 report closure |
| EC-003 | S01/S02 | edge | requirement EC-003 | CI/head blockers keep priority over carryover policy | stale head, CI pending/running/failed/none, blocking limitations | review policy overriding CI/head state | yes | covered-existing plus targeted regression | S01/S02 report closure |
| EC-004 | S01/S02 | edge | requirement EC-004 | Empty-inventory, no completion, latency-satisfied path remains `review_completion_unknown` | no carryover, no current selected feedback, completion none, latency true | regression in existing unknown path | yes | covered-existing | S01/S02 report closure |

Risk-calibrated coverage:

- Wrapper-level JSON tests are preferred because the public scripts are the downstream contract.
- Private helper tests are acceptable only as supplemental diagnostics.
- Live GitHub integration is not required; fake `gh` and fake snapshot fixtures are sufficient for this classification issue.
- `pr_review_snapshot.py` collector tests should remain focused on inventory inclusion/exclusion, not lifecycle terminal policy.

## 7. Review Gates

- Per-step gate: each S01/S02/S03/S90/S99 step must complete report update, reviewer gate, then commit or approved no-op before the next step starts.
- S01 reviewer: `code-reviewer`, test sensitivity and Issue187 supersession.
- S02 reviewer: `code-reviewer`, runtime JSON compatibility and minimal classification diff.
- S03 reviewer: `spec-reviewer` for docs; `code-reviewer` if mirror runtime files are touched.
- S90 reviewer: `spec-reviewer`, evidence adoption and docs impact.
- S99 reviewers: `qa-reviewer`, issue-wide `code-reviewer`, `spec-reviewer`.

Delegated worker output is never a substitute for reviewer pass. This draft is also not a substitute for canonical plan review.

## 8. Rollback / Compatibility

- Rollback unit: revert S02 runtime classification helpers and S03 docs updates together with S01 tests if Issue219 is abandoned.
- Compatibility goal: do not introduce a new top-level status or combined reason string unless a plan amendment approves it.
- Backward-compatible optional field: `decision.actionable_inventory_reason` may be added only if needed to preserve carryover machine readability while keeping primary `status_reason` lifecycle-oriented.
- Existing contract preserved:
  - current selected feedback remains immediate feedback handling,
  - fallback issue comment remains low-confidence,
  - CI/head blockers remain priority,
  - outdated/unavailable threads do not become actionable inventory,
  - `review_completion_unknown` stays non-pass human gate.

## 9. Docs Impact

- Required docs impact:
  - `SKILL.md` must describe current review lifecycle and actionable inventory as two axes.
  - `review_completion_unknown` wording must not require the entire actionable inventory to be empty; it must require no current-boundary selected actionable feedback and no trusted completion after latency guards.
  - `selected_unresolved_count == 0` must continue to warn that no-review-work is not proven.
- Report impact:
  - record Issue187 expectation update/supersession,
  - record provider/mirror resolution,
  - record final closure evidence by AC/EC.
- No release note or ADR is required unless implementation discovers a new public status taxonomy or downstream-breaking field change.

## 10. Final Quality Gate

Final exit contract:

- All Spec-Locked Closure Index rows AC-001..AC-006 and EC-001..EC-004 have report evidence.
- S01-S03/S90 have per-step reviewer pass or approved no-op records.
- Focused tests and `uv run pytest tests/unit` pass, or any failure is proven unrelated and accepted by reviewer.
- `./spec-dock/scripts/spec-dock validate` and `git diff --check` pass.
- `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` pass.
- Report records final commit/no-op evidence.
- No canonical phase promotion or issue finish occurs until the main orchestrator performs the official workflow.

## 11. Plan Blockers

- none blocking from reviewed requirement/design evidence.

Non-blocking implementation choices:

- Whether to add `decision.actionable_inventory_reason` remains an S02 minimal-diff choice. If added, update fingerprint/tests/docs.
- Whether dogfooding mirror runtime files are synchronized in S03 or recorded as pending depends on the repo's accepted provider-to-mirror workflow at execution time.

Plan amendment triggers:

- A new top-level status, new primary `status_reason`, or changed fallback issue comment policy is needed.
- GitHub collection scope, authentication, or thread data model must change.
- Current selected feedback cannot remain immediate feedback while satisfying AC-001/AC-003.
- Existing public downstream consumers require a different machine-readable carryover field than counts/ids or optional `actionable_inventory_reason`.
- S01 cannot express the required behaviors through public wrapper-level or existing fake-fixture tests.
- Any required closure index row must be deleted, weakened, or moved to manual-only evidence.

## 12. Integration Notes for Main Orchestrator

- Adopt only after a post-run diff guard confirms this draft is the only new direct child Markdown file created by the delegated implementation-planner.
- If adopted, integrate into canonical `plan.md` by the main orchestrator only, then record adoption in `report.md`.
- Preserve this draft metadata as `adoption_status: unreviewed`, `reflected_to: []`, and `diff_guard_result: pending`; do not back-edit this delegated file to claim adoption.
- Fresh `spec-reviewer` pass remains required after canonical plan integration.
- Implementation should start only after canonical plan review passes; this draft itself does not claim implementation readiness.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
