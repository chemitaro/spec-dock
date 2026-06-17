---
artifact_kind: disc
created_by_role: implementation-planner
scope_id: iss-00187
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/reference_deps.md
  - spec-dock/docs/reference_sync.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260615t154753z-01-research-actions-ci-observation-scope.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260615t154753z-02-interview-actions-only-pass-contract.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: partially_adopted
reflected_to:
  - requirement.md
  - design.md
  - plan.md
  - report.md
diff_guard_result: pending
---

# PR Review Completion Signal Contract Plan Evidence

This draft is source-grounded planning evidence only. It does not change canonical issue docs, source, tests, GitHub state, reviewer status, or issue readiness.

## 1. Plan Summary

PR #190 head `fc3041f86a7f9defba2d3fd8b48ff1c48126151a` reportedly had CI passed and matched the requested head, but `wait_pr_observation.sh` timed out because the Codex review lifecycle `completion_signal` remained `none`. Earlier head `66c6a3be199a30ea0104816361822de5ddda80a5` reached current Codex review findings through `submitted_pull_request_review` and unresolved review threads, which the existing contract handles.

The gap is narrower than CI state observation: the review lifecycle currently treats a current Codex-authored pull request review as high-confidence completion, a current Codex-authored issue comment as low-confidence fallback, and the absence of both as missing completion. This leaves no high-confidence terminal signal for a no-findings Codex review form when no pull request review object is posted.

The implementation plan should be gated as a scope amendment or follow-up issue before code starts, because current `iss-00187` canonical scope says Codex review lifecycle observation is out of scope. If adopted, the smallest executable fix is to add a new explicit no-findings completion signal contract in `fetch_pr_review_snapshot.sh`, then teach snapshot/wait wrappers that this signal can complete observation only under strict current-boundary, no-feedback, no-open-thread, and CI-passed conditions.

## 2. Requirement / Design Traceability

- Current issue requirement target: move CI observation to Actions read and avoid impossible Checks-read remediation.
- Current issue explicit non-scope: Codex review comment / review thread collector specification changes and Codex review lifecycle observation changes.
- Current design target: `fetch_pr_checks_snapshot.sh` Actions-primary CI collector, wrapper classification, provider/mirror consistency, and fake `gh` regression tests.
- Current report evidence: PR #190 follow-ups through head `66c6a3be...` are recorded as CI contract fixes, not review-completion fixes.
- Existing review lifecycle implementation:
  - `fetch_pr_review_snapshot.sh` marks `completion_signal="submitted_pull_request_review"` when there is a current Codex-authored pull review in `commented`, `approved`, or `changes_requested`.
  - It marks `completion_signal="fallback_issue_comment"` for any current Codex-authored issue comment and keeps it low confidence.
  - It records `fallback_pass_candidate.present=true` for allowlisted `No major issues found` issue comments, but `promotes_top_level_status=false`.
  - It marks `completion_signal="none"` when no current completion signal is found.
  - `fetch_pr_observation_snapshot.sh` and `wait_pr_observation.sh` keep `fallback_issue_comment` as `human_gate` / `wait_or_resume`, and keep `none` as pending until timeout.
- Therefore, a no-findings Codex form with no pull request review object currently has no path to `merge_prepared`, even when CI is passed and head freshness is clean.

## 3. Milestones

- M0 Scope gate:
  - Decide whether this work is an amendment to `iss-00187` or a new follow-up issue. Current canonical docs need updating before implementation because the review lifecycle is currently out of scope.
- M1 Characterization:
  - Add failing fake-`gh` coverage for the exact no-findings no-PR-review form, using only local fixtures and no network calls.
  - If the real GitHub shape is unknown, first encode the user-provided `fc3041...` symptom as a contract test that reproduces `completion_signal="none"` and `wait_pr_observation.sh` timeout.
- M2 Review collector contract:
  - Introduce an explicit high-confidence no-findings completion signal, for example `codex_no_findings_completion`, only when evidence is current-boundary, Codex-authored, allowlisted, after the trigger, and not stale.
- M3 Wrapper completion behavior:
  - Update `fetch_pr_observation_snapshot.sh` and `wait_pr_observation.sh` to treat the new signal as complete when CI is passed and no current selected unresolved thread or changes-requested evidence exists.
- M4 Safety tests:
  - Add negative tests proving generic fallback issue comments, old comments, stale-head signals, pending review requests, unresolved current threads, changes-requested reviews, and blocking collection failures do not pass.
- M5 Docs/mirror:
  - Update provider `SKILL.md` only if operator-facing behavior changes. Sync `.agents/...` dogfooding copies after provider source changes.
- M6 Final gates:
  - Run focused regression, full `test_init_update.py` if risk warrants, provider/mirror comparison, `git diff --check`, `spec-dock validate`, and reviewer gates.

## 4. Dependency-Derived Execution Order

1. Scope amendment before implementation:
   - Target: canonical `requirement.md`, `design.md`, `plan.md`, `report.md` by main orchestrator only.
   - Reason: the current issue explicitly excludes Codex review lifecycle changes.
2. Characterization tests before code:
   - Target: `tests/unit/infra/test_init_update.py`.
   - Reason: the known bug is a completion contract gap. A failing end-to-end fake-`gh` scenario must pin the exact JSON branch before altering lifecycle semantics.
3. Collector signal before wrappers:
   - Target: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`.
   - Reason: wrappers consume `decision.completion_signal` and `codex_review.lifecycle.completion_signal`; they should not infer raw comment semantics independently.
4. Wrapper classification after collector:
   - Target: `fetch_pr_observation_snapshot.sh`, then `wait_pr_observation.sh`.
   - Reason: snapshot creates the single-poll normalized contract; wait should only poll/classify that contract.
5. Mirror after provider:
   - Target: `.agents/skills/github-pr-observation/scripts/...`.
   - Reason: provider-side install root is the shipped asset authority; dogfooding mirror is validation surface.
6. Final issue-wide verification:
   - Target: focused and broad tests plus validation and reviewers.
   - Reason: this contract affects PR merge-preparer readiness decisions.

## 5. Issue / Step Slicing

Recommended step slices if adopted into `iss-00187`:

- S04-review-characterization:
  - Behavior goal: reproduce no-findings Codex completion with no pull request review and show current output is not merge-ready.
  - Target files: `tests/unit/infra/test_init_update.py`.
  - Closure IDs: `tc-s04-001`, `tc-s04-002`.
  - Commit slice: test-only red characterization.
- S05-review-collector-signal:
  - Behavior goal: collector emits an explicit current-boundary no-findings completion signal with high confidence and sanitized provenance.
  - Target files: provider `fetch_pr_review_snapshot.sh`, focused tests.
  - Closure IDs: `tc-s05-001` through `tc-s05-005`.
  - Commit slice: collector + tests.
- S06-review-wrapper-completion:
  - Behavior goal: snapshot and wait wrappers complete observation when CI passed plus the new no-findings signal is present, and preserve wait/human_gate for all unsafe cases.
  - Target files: provider `fetch_pr_observation_snapshot.sh`, `wait_pr_observation.sh`, focused tests.
  - Closure IDs: `tc-s06-001` through `tc-s06-004`.
  - Commit slice: wrappers + tests.
- S90-docs-mirror:
  - Behavior goal: provider docs and dogfooding mirror match the adopted signal contract.
  - Target files: provider `SKILL.md` only if operator-facing wording changes; `.agents/...` mirror scripts.
  - Closure IDs: `tc-s90-review-001`, `tc-s90-review-002`.
  - Commit slice: docs/mirror.
- S99-final-quality:
  - Behavior goal: issue-wide verification and reviewer gates close all review-completion closure IDs.
  - Target files: report evidence by orchestrator only, no behavior changes unless reviewers find gaps.
  - Closure ID: `tc-s99-review-001`.

Alternative slicing if kept outside `iss-00187`:

- Create a follow-up issue under `epic-00158` for "Codex Review No Findings Completion Signal".
- Use this draft as planning evidence for that issue's requirement/design/plan.
- Keep `iss-00187` limited to Actions CI state and record the review-completion timeout as a non-blocking follow-up or blocker, depending on PR #190 delivery needs.

## 6. Test Strategy Mapping

- `tc-s04-001` characterization: no PR review, no fallback comment, CI passed, head matched, lifecycle `none`.
  - Expected before fix: snapshot returns `pending` / `missing_current_completion_signal`; wait times out with `wait_or_resume`.
  - Verification: fake `gh` snapshot/wait test in `tests/unit/infra/test_init_update.py`.
- `tc-s04-002` characterization: no PR review, current Codex-authored no-findings issue comment.
  - Expected before fix if using the existing fallback form: `completion_signal="fallback_issue_comment"`, `fallback_pass_candidate.present=true`, `promotes_top_level_status=false`, wrapper stays `human_gate`.
  - Verification: extend existing issue_182/issue_176 fallback tests.
- `tc-s05-001` acceptance: allowlisted no-findings evidence after the explicit trigger emits `completion_signal="codex_no_findings_completion"` with high or explicitly named confidence.
  - Expected: selected no-findings source IDs are present; generic fallback comments are not selected.
- `tc-s05-002` negative: arbitrary Codex issue comments remain `fallback_issue_comment` and low confidence.
  - Expected: no promotion, no `merge_prepared`.
- `tc-s05-003` negative: pre-trigger or inferred/unknown-boundary no-findings comments do not complete.
  - Expected: `completion_signal` remains `none` or low-confidence fallback.
- `tc-s05-004` negative: unresolved current review thread or current changes-requested evidence wins over no-findings completion.
  - Expected: `human_gate` / `address_review_feedback`.
- `tc-s05-005` negative: collection failure or unparseable trigger timestamp blocks completion.
  - Expected: `unknown` / `human_gate`, no pass.
- `tc-s06-001` integration: snapshot returns `passed`, `merge_prepared`, `observation_complete=true` when CI passed and new no-findings completion signal is present.
- `tc-s06-002` integration: wait exits successfully without timeout for the same payload.
- `tc-s06-003` regression: `fallback_issue_comment` still returns `human_gate` / `wait_or_resume`.
- `tc-s06-004` regression: `completion_signal="none"` still waits and can time out.

Suggested focused commands:

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "no_findings or completion_signal or fallback_issue_comment or missing_current_completion_signal"
uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"
git diff --check
./spec-dock/scripts/spec-dock validate
```

Run `uv run pytest tests/unit/infra/test_init_update.py` if wrapper behavior or shared fake-`gh` helpers change broadly.

## 7. Review Gates

- Scope gate:
  - `spec-reviewer` must pass any canonical requirement/design/plan amendment before implementation starts.
- Per-step code gate:
  - S04/S05/S06 require `code-reviewer` pass because they change runtime script behavior and tests.
- Docs/mirror gate:
  - S90 requires `spec-reviewer` if `SKILL.md` wording changes, and code-reviewer or mechanical inspection for provider/mirror script equality.
- Final gates:
  - `qa-reviewer`: confirms test sufficiency for no-findings, fallback, missing-signal, unresolved-thread, and stale/boundary cases.
  - issue-wide `code-reviewer`: confirms wrapper classification cannot false-pass unsafe review states.
  - final `spec-reviewer`: confirms canonical docs, this evidence, implementation, tests, and report closure align.
- PR observation gate:
  - After push, rerun the same PR observation boundary for the latest head SHA only. Do not reuse older head observations as current completion evidence.

## 8. Rollback / Compatibility

- Rollback:
  - Revert the S05/S06 commits to restore current conservative behavior where only submitted pull request reviews can complete and issue-comment fallback remains human-gated.
- Compatibility:
  - Keep existing `submitted_pull_request_review`, `fallback_issue_comment`, and `none` values unless a canonical design amendment approves renaming.
  - Prefer adding a new signal value over changing the meaning of `fallback_issue_comment`.
  - Preserve output keys: `review`, `decision`, `codex_review.lifecycle`, `decision_fingerprint`, `audit_fingerprint`, `limitations`, and stdout JSON authority.
  - Keep diagnostics on stderr and avoid raw body/token leaks in default body modes.
- False-pass guard:
  - The new signal must be accepted only for strict no-findings evidence. Generic positive comments, inferred trigger boundary, stale comments, unresolved threads, changes requested, blocking collection failures, draft PRs, non-open PRs, stale head, or non-passed CI must not become merge-ready.

## 9. Docs Impact

- Canonical docs:
  - `requirement.md`: add or follow up a requirement for no-findings Codex completion without PR review; remove the current out-of-scope conflict only if this stays in `iss-00187`.
  - `design.md`: define the new signal value, source evidence, confidence, body/boundary requirements, and wrapper classification.
  - `plan.md`: add S04/S05/S06/S90/S99 closure IDs and concrete test cards.
  - `report.md`: record this draft in Delegated Draft Evidence and Evidence Adoption Ledger if adopted.
- Provider docs:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md` may need a short operator note that no-findings Codex completion can be recognized without a pull request review only through the explicit signal contract.
- Mirror:
  - After provider changes, sync `.agents/skills/github-pr-observation/` and verify `cmp` for changed scripts/docs.

## 10. Final Quality Gate

The final quality gate should not pass until all of the following are true:

- The scope conflict is resolved in canonical docs or a follow-up issue owns the work.
- Characterization tests fail before implementation or the report explains why existing evidence is the sensitivity proof.
- Focused tests cover no-findings completion, fallback non-promotion, missing completion timeout, unresolved current threads, changes requested, trigger-boundary safety, stale/head safety, and collection failure safety.
- Required focused command and `git diff --check` pass.
- `./spec-dock/scripts/spec-dock validate` passes, or any failure is unrelated and recorded.
- Provider and dogfooding mirror changed scripts match after S90.
- Per-step and final reviewer gates pass fresh.
- PR observation is rerun against the latest PR head SHA and reports a current completion signal that matches the new contract.

## 11. Plan Blockers

- Blocking: current `iss-00187` requirement and design explicitly exclude Codex review lifecycle changes. Implementing this plan inside `iss-00187` requires canonical amendment and fresh `spec-reviewer` pass, or a new follow-up issue.
- Blocking until characterized: the exact no-findings "form" payload for head `fc3041...` is not present in local checked-in evidence. The first executable work unit must pin the observed GitHub shape with a fake-`gh` fixture or attach a sanitized local snapshot.
- Open decision: should an allowlisted no-findings issue comment be upgraded from low-confidence fallback, or should the new completion signal require a distinct non-comment evidence source? The safer default is a new explicit signal value, not reusing `fallback_issue_comment`.
- Open decision: should the new signal be named `codex_no_findings_completion`, `no_findings_issue_comment`, or another value? The design should choose a machine-stable name before tests are written.
- Open decision: if no PR review and no issue comment are posted, what local observable GitHub artifact proves completion? If none exists, the correct behavior remains wait/timeout and the product fix must change trigger/review emission rather than observation.

## 12. Integration Notes for Main Orchestrator

- Changed discussion artifact path:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t000000z-04-planner-pr-review-completion-signal-contract.md`
- Source requirement/design revisions:
  - Active issue docs read from `spec-dock/active/issue/{requirement,design,plan,report}.md` on 2026-06-16 in the current worktree.
  - Existing canonical issue docs already include implementation/report evidence through PR #190 head `66c6a3be...`; no local evidence for `fc3041...` was found.
- Lightweight provenance summary:
  - Sources inspected: active context, active issue/epic docs, existing issue discussions, workflow/plan references, provider review/snapshot/wait scripts, dogfooding script equality, and relevant fake-`gh` tests.
  - Leaf evidence used: none. No depth=2 leaf delegation was requested or used.
  - Network commands: none.
  - Forbidden actions avoided: no canonical docs edited, no source/test files edited, no GitHub mutation, no commits, no phase promotion, no reviewer-pass claim, no implementation-readiness claim.
- Unresolved design gaps:
  - The exact no-findings no-PR-review GitHub payload shape is not locally available.
  - Current canonical scope conflicts with review-lifecycle implementation.
  - The stable signal name and acceptable high-confidence evidence source need canonical design adoption.
- Handoff statement:
  - No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
