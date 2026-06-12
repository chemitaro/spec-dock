---
種別: draft-plan
ID: "20260612t021000z-draft-plan"
タイトル: "PR observation boundary implementation plan draft"
状態: "draft"
created_by_role: "implementation-planner"
scope_id: "iss-00182"
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
authority: "proposed"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "pending_orchestrator_review"
---

# PR observation boundary implementation plan draft

## 1. Plan Summary

This draft proposes an executable implementation plan for `iss-00182`. It is evidence for the main orchestrator to review and possibly integrate into canonical `plan.md`; it is not a canonical plan.

Goal: make `github-pr-observation` final status, recommended action, wait stability, and progress depend on the current trigger / resume boundary decision artifacts only. Historical / all-fetched review context remains available as explicitly non-authoritative audit context.

Primary implementation source-of-truth:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`

Existing test candidate location:

- `tests/unit/infra/test_init_update.py`
  - Existing GitHub PR observation script tests already exercise fake `gh`, review collector behavior, snapshot classification, wait progress / fingerprint loops, fallback issue comments, trigger boundary handling, and install-root asset inventory.

Proposed implementation order follows the design dependency chain:

1. Collector output contract and fingerprints.
2. One-shot snapshot classification from the decision surface.
3. Wait-loop stability and progress from the decision fingerprint / decision counts.
4. Shipped skill docs and output semantics.
5. Final docs, QA, code review, and spec review gates.

Each implementation step is intended as `1 step = 1 review scope = 1 commit`.

## 2. Requirement / Design Traceability

Requirement trace:

- AC-001: S01 adds current decision and audit separation; S02 and S03 use only decision-scoped fields for final status, action, progress, and stability.
- AC-002: S01 exposes selected current unresolved thread ids/count; S02 and S03 classify those as current review feedback blockers.
- AC-003: S02 and S03 preserve `fallback_issue_comment` as top-level `human_gate` / `wait_or_resume`.
- AC-004: S01 emits `fallback_pass_candidate` for current boundary no-major-issues fallback issue comments; S02 mirrors it into final decision output.
- AC-005: S01 emits `decision_fingerprint` and `audit_fingerprint`; S03 uses decision fingerprint for wait stability.
- AC-006: S04 documents final decision, current, audit, fallback, and fingerprint semantics in the shipped skill.

Design trace:

- The design establishes three surfaces: `decision`, `review.current`, and `review.audit`.
- The design fixes Option C: fallback issue comments do not promote top-level pass, but no-major-issues fallback comments become observable as `fallback_pass_candidate`.
- The design requires trigger identity in decision fingerprint input, with historical-only changes excluded from wait stability.
- The design prefers additive migration and legacy field compatibility.

## 3. Milestones

- M01: Collector contract locked.
  - Outcome: `fetch_pr_review_snapshot.sh` emits decision/current/audit surfaces and split fingerprints without deleting legacy debug fields.
- M02: Snapshot classification locked.
  - Outcome: `fetch_pr_observation_snapshot.sh` derives final status/action/reason from `decision` plus CI/head/limitations.
- M03: Wait behavior locked.
  - Outcome: `wait_pr_observation.sh` uses decision fingerprint for stability and decision/current counts for progress.
- M04: Public semantics locked.
  - Outcome: `SKILL.md` documents authoritative vs audit surfaces and fallback policy.
- M99: Final quality gates.
  - Outcome: docs impact resolved, test sufficiency reviewed, issue-wide code review passed, spec review passed.

## 4. Dependency-Derived Execution Order

1. `fetch_pr_review_snapshot.sh` is upstream because it owns selected/current/audit review data and collector fingerprints.
2. `fetch_pr_observation_snapshot.sh` depends on the collector output contract and should not invent a parallel decision model.
3. `wait_pr_observation.sh` depends on snapshot shape and collector decision fingerprint to avoid historical-only wait instability.
4. `SKILL.md` follows implementation behavior so docs match actual output semantics.
5. Final gates run after all behavior and docs changes are integrated.

## 5. Issue / Step Slicing

### Spec-Locked Closure Index proposal

| id | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | owner step |
|---|---|---|---|---|---|---|---|
| cli-001 | AC-001, EC-003 | Historical unresolved threads remain audit-only when selected current unresolved thread ids are empty | explicit trigger, old unresolved thread, current fallback issue comment | historical blocker contaminates final decision | yes | red-required | S01, S02 |
| cli-002 | AC-002 | Current selected unresolved thread ids drive `human_gate` / `address_review_feedback` | explicit trigger, current selected unresolved Codex thread | current review feedback ignored | yes | red-required | S01, S02, S03 |
| cli-003 | AC-003 | `fallback_issue_comment` does not produce top-level pass / complete | CI passed, head matched, limitations empty, selected unresolved count 0, fallback issue comment | low-confidence issue comment over-promotes merge readiness | yes | red-required | S02, S03 |
| cli-004 | AC-004 | no-major-issues fallback comment is observable as `fallback_pass_candidate` and `promotes_top_level_status=false` | current boundary Codex issue comment body indicates no major issues | useful current fallback signal hidden | yes | red-required | S01, S02 |
| cli-005 | AC-005 | `decision_fingerprint` is stable across historical-only thread changes; `audit_fingerprint` may change | same current decision, changed historical thread payload | wait loop resets on audit-only changes | yes | red-required | S01, S03 |
| cli-006 | AC-006 | shipped skill docs name authoritative and audit-only surfaces | post-change `SKILL.md` | downstream agent misreads output contract | yes | inspect-only | S04 |
| cli-007 | EC-001 | inferred trigger keeps confidence/limitation visible and does not mix historical context into decision | inferred trigger snapshot | inferred boundary treated as fully explicit | yes | covered-existing plus update | S01, S02 |
| cli-008 | EC-002 | no current completion signal and no fallback remains safe-side wait/pending/human-gate, not pass | CI passed, no selected review, no fallback | missing signal becomes false pass | yes | red-required | S02, S03 |
| cli-009 | EC-004 | legacy `review.threads` / `review.codex_authored` remain available with explicit all-fetched/non-authoritative scope metadata | snapshot payload with historical context | breaking debug consumers or ambiguous legacy fields | yes | red-required | S01 |

### S01 behavior slice: collector emits decision/current/audit surfaces

Behavior goal:

- Convert existing selected/current calculations in `fetch_pr_review_snapshot.sh` into authoritative `decision` and `review.current` surfaces, keep all-fetched context in `review.audit`, and split `decision_fingerprint` from `audit_fingerprint`.

Planned contract:

- Scope:
  - Allowed: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - Tests: `tests/unit/infra/test_init_update.py`
- Test obligation:
  - Cover AC-001, AC-002, AC-004, AC-005, EC-001, EC-004.
  - Include regression cases for historical unresolved thread, current selected unresolved thread, fallback candidate, fingerprint split, and legacy scope metadata.
- Red or alternative evidence requirement:
  - `red-required` for new output fields and fingerprint behavior.
  - Existing tests such as `test_issue_176_s03_review_collector_returns_codex_review_contract`, `test_issue_176_s03_review_collector_does_not_mark_fallback_as_primary`, and `test_issue_75_pr_observation_review_collector_explicit_trigger_body_caps_and_threads` are candidate anchors, but new assertions should fail before implementation.
- Green verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "review_collector or pr_observation_review_collector or issue_176_s03"`
- Refactor guardrail:
  - Keep changes additive where possible. Do not delete legacy `review.threads`, `review.signals`, or `review.codex_authored`; mark them with scope / decision-authoritative metadata.
- Amendment trigger:
  - If `review.codex_authored` must change shape from list to object and breaks existing tests/consumers, stop for orchestrator decision or plan amendment.

Delegation contract:

- delegated role: `dev-coder`
- input docs:
  - `requirement.md`, `design.md`, this plan after adoption, research/interview/design draft discussions, target script.
- allowed changes:
  - collector script plus focused tests in `tests/unit/infra/test_init_update.py`.
- forbidden changes:
  - `fetch_pr_observation_snapshot.sh`, `wait_pr_observation.sh`, `SKILL.md`, canonical docs, unrelated install/update behavior.
- acceptance criteria:
  - `decision.scope`, `decision.trigger`, selected ids/counts, `fallback_pass_candidate`, `review.current`, `review.audit`, legacy scope metadata, `decision_fingerprint`, and `audit_fingerprint` are present and match design semantics.
- required verification:
  - targeted pytest command above; broaden to `uv run pytest tests/unit/infra/test_init_update.py` if adjacent tests fail from intended payload shape changes.
- reviewer focus:
  - per-step `code-reviewer`, focusing on output compatibility, shell/Python embedded JSON correctness, and no secret/body leakage regression.
- stop conditions:
  - selected current thread semantics contradict approved design; fallback candidate phrase matching needs broad NLP; legacy field migration becomes breaking.
- output required:
  - changed files, tests added/updated, verification output, unresolved risk, `Ledger Note` or `No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s01-001` acceptance: historical thread is audit-only
  - 前提: explicit trigger after an old unresolved Codex thread; no selected current thread.
  - 操作: run `fetch_pr_review_snapshot.sh` through fake `gh`.
  - 期待結果: `decision.selected_unresolved_count == 0`, old thread appears under `review.audit` or legacy all-fetched fields with non-authoritative scope, and not under `review.current.selected_unresolved_thread_ids`.
  - 失敗検出: old unresolved thread changes decision-facing count or decision fingerprint.
  - 検証方法: add/update `tests/unit/infra/test_init_update.py` collector test.
  - 関連 closure id: `cli-001`, `cli-009`

- `tc-s01-002` acceptance: current selected unresolved thread is decision-facing
  - 前提: explicit trigger with selected Codex review comment linked to an unresolved thread after trigger.
  - 操作: run collector with fake PR review/comment/thread payload.
  - 期待結果: `decision.selected_unresolved_thread_ids` and `selected_unresolved_count` contain the selected thread; `review.current` includes it.
  - 失敗検出: current selected thread only appears in all-fetched audit data.
  - 検証方法: extend existing `test_issue_176_s03_review_collector_returns_codex_review_contract` pattern.
  - 関連 closure id: `cli-002`

- `tc-s01-003` acceptance: fallback pass candidate is explicit and non-promoting
  - 前提: current boundary Codex issue comment says no major issues; no submitted PR review.
  - 操作: run collector.
  - 期待結果: `decision.fallback_pass_candidate.present == true`, source id is the issue comment, `promotes_top_level_status == false`, lifecycle remains `fallback_issue_comment`.
  - 失敗検出: candidate missing, or lifecycle becomes primary submitted review.
  - 検証方法: update `test_issue_176_s03_review_collector_does_not_mark_fallback_as_primary` or add sibling test.
  - 関連 closure id: `cli-004`

- `tc-s01-004` acceptance: decision and audit fingerprints split
  - 前提: two fake runs with identical decision artifacts and changed historical-only thread.
  - 操作: run collector twice or construct two fake outputs via test helper.
  - 期待結果: `decision_fingerprint` unchanged, `audit_fingerprint` changed, top-level collector compatibility fingerprint behavior is documented by assertions.
  - 失敗検出: historical-only change resets decision fingerprint.
  - 検証方法: new collector test in `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: `cli-005`

Step closure contract:

- Close when all required S01 closure ids pass, legacy debug fields remain observable, and per-step code review passes.

Report evidence destination:

- `report.md` session log, TDD evidence, Step Contract Closure rows for `cli-001`, `cli-002`, `cli-004`, `cli-005`, `cli-009`, Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.

### S02 behavior slice: snapshot classification reads decision surface

Behavior goal:

- Update `fetch_pr_observation_snapshot.sh` so final status, `recommended_next_action`, `status_reason`, `observation_complete`, and top-level fingerprint derive from collector `decision` plus CI/head/limitations, not mixed `review.threads` or all-fetched context.

Planned contract:

- Scope:
  - Allowed: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - Tests: `tests/unit/infra/test_init_update.py`
- Test obligation:
  - Cover AC-001, AC-002, AC-003, AC-004, EC-002 and CI/head/limitation precedence.
- Red or alternative evidence requirement:
  - `red-required` for final JSON classification and top-level fingerprint source.
- Green verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_snapshot or fetch_pr_observation_snapshot or fallback_issue_comment or review_collector"`
- Refactor guardrail:
  - Do not duplicate collector selection logic. Snapshot should consume the collector decision contract and apply CI/head/limitation precedence.
- Amendment trigger:
  - If status taxonomy from design is insufficient for a real classification branch, record a plan/design gap instead of inventing new unreviewed status values.

Delegation contract:

- delegated role: `dev-coder`
- input docs:
  - approved requirement/design/plan, S01 output contract, snapshot script.
- allowed changes:
  - snapshot script plus focused tests.
- forbidden changes:
  - collector output contract changes beyond S01 accepted shape, wait script, docs, canonical docs.
- acceptance criteria:
  - historical unresolved thread cannot drive `address_review_feedback`; current selected unresolved thread can; fallback issue comment remains `human_gate` / `wait_or_resume`; `fallback_pass_candidate` is visible; top-level `fingerprint` or `decision_fingerprint` uses decision inputs.
- required verification:
  - targeted pytest command above; include full `tests/unit/infra/test_init_update.py` if snapshot helper changes are shared.
- reviewer focus:
  - per-step `code-reviewer`, focusing on classification precedence and compatibility of top-level fields.
- stop conditions:
  - Snapshot cannot reliably distinguish decision vs audit because S01 output is absent or stale; top-level fingerprint compatibility policy is unclear.
- output required:
  - changed files, tests added/updated, verification output, unresolved risk, ledger note.

#### 具体テストケース一覧

- `tc-s02-001` acceptance: historical unresolved thread does not drive final action
  - 前提: collector output has `decision.selected_unresolved_count == 0`, legacy/audit thread unresolved count is 1, CI passed, head matched, fallback issue comment present.
  - 操作: run snapshot script with fake collector and checks payload.
  - 期待結果: top-level `recommended_next_action == "wait_or_resume"` and `status_reason == "fallback_issue_comment_low_confidence"`, not `address_review_feedback`.
  - 失敗検出: all-fetched unresolved count drives feedback action.
  - 検証方法: new snapshot test in `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: `cli-001`, `cli-003`

- `tc-s02-002` acceptance: current selected unresolved thread drives review feedback
  - 前提: collector `decision.selected_unresolved_thread_ids` has one current selected thread, CI passed, head matched.
  - 操作: run snapshot.
  - 期待結果: top-level `human_gate`, `recommended_next_action == "address_review_feedback"`, `decision.status_reason == "current_selected_unresolved_thread"`.
  - 失敗検出: selected current blocker is ignored because legacy `review.status` is approved/commented/none.
  - 検証方法: snapshot fake collector test.
  - 関連 closure id: `cli-002`

- `tc-s02-003` acceptance: fallback pass candidate stays non-promoting
  - 前提: CI passed, head matched, no selected unresolved thread, current fallback no-major-issues comment.
  - 操作: run snapshot.
  - 期待結果: top-level remains `human_gate`, `recommended_next_action == "wait_or_resume"`, `observation_complete is false`, and `decision.fallback_pass_candidate.present is true`.
  - 失敗検出: fallback issue comment produces `passed`, `merge_prepared`, or `observation_complete true`.
  - 検証方法: snapshot test.
  - 関連 closure id: `cli-003`, `cli-004`

- `tc-s02-004` negative: missing current completion signal is not pass
  - 前提: CI passed, head matched, limitations empty, no selected review and no fallback comment.
  - 操作: run snapshot.
  - 期待結果: safe-side pending/wait/human-gate result per design, never top-level pass.
  - 失敗検出: absence of evidence becomes success.
  - 検証方法: snapshot test.
  - 関連 closure id: `cli-008`

Step closure contract:

- Close when snapshot final JSON uses decision-scoped classification for all required branches, S02 tests pass, and per-step code review passes.

Report evidence destination:

- `report.md` session log, TDD evidence, Step Contract Closure rows for `cli-001`, `cli-002`, `cli-003`, `cli-004`, `cli-008`, Test Contract Closure, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate.

### S03 behavior slice: wait stability and progress are decision-scoped

Behavior goal:

- Update `wait_pr_observation.sh` so `semantic_fingerprint()`, same-fingerprint stability, final wait payload fingerprint, and progress summaries use the decision fingerprint and decision/current counts, not audit-only fields.

Planned contract:

- Scope:
  - Allowed: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - Tests: `tests/unit/infra/test_init_update.py`
- Test obligation:
  - Cover AC-001, AC-002, AC-003, AC-005 and progress semantics.
- Red or alternative evidence requirement:
  - `red-required` for historical-only change not resetting stability.
- Green verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or wait_pr_observation or issue_174"`
- Refactor guardrail:
  - Keep resume/trigger behavior unchanged. Do not modify `trigger_codex_review.sh`.
- Amendment trigger:
  - If progress output must show audit counts for user usefulness, require explicit audit label and docs alignment; otherwise omit audit counts.

Delegation contract:

- delegated role: `dev-coder`
- input docs:
  - approved requirement/design/plan, S01/S02 contracts, wait script.
- allowed changes:
  - wait script plus focused tests.
- forbidden changes:
  - trigger helper behavior, GitHub write semantics, snapshot classifier changes outside S02, docs/canonical docs.
- acceptance criteria:
  - wait uses `decision_fingerprint` when present; historical-only audit changes do not reset same-fingerprint stability; progress reflects decision/current selected counts; fallback issue comment remains terminal human gate but not complete/pass.
- required verification:
  - targeted pytest command above, plus full `tests/unit/infra/test_init_update.py` if shared helpers are edited.
- reviewer focus:
  - per-step `code-reviewer`, focusing on wait loop terminal/stability semantics, progress non-authority, and timeout/resume compatibility.
- stop conditions:
  - Stable wait requires a new output field not provided by S01/S02; existing timeout/resume contract conflicts with decision fingerprint.
- output required:
  - changed files, tests added/updated, verification output, unresolved risk, ledger note.

#### 具体テストケース一覧

- `tc-s03-001` acceptance: historical-only changes do not reset wait stability
  - 前提: fake snapshot sequence with same decision fingerprint and changed audit/legacy thread payload.
  - 操作: run wait in resume mode with `--same-fingerprint-count 2`.
  - 期待結果: `same_fingerprint_observed` advances across audit-only change and final fingerprint equals decision fingerprint.
  - 失敗検出: wait treats audit-only change as semantic change and times out or resets count.
  - 検証方法: extend `_issue_174_run_wait_fake_snapshots` style helper in `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: `cli-005`

- `tc-s03-002` acceptance: wait progress uses decision/current counts
  - 前提: fake snapshot has audit unresolved count 1, decision selected unresolved count 0, fallback issue comment.
  - 操作: run wait with stderr progress.
  - 期待結果: progress does not present historical unresolved count as decision blocker; final action is `wait_or_resume`.
  - 失敗検出: progress line suggests unresolved current blocker from audit count.
  - 検証方法: wait progress test.
  - 関連 closure id: `cli-001`, `cli-003`

- `tc-s03-003` acceptance: current selected unresolved thread remains terminal human gate
  - 前提: fake snapshot has decision selected unresolved thread id and CI passed.
  - 操作: run wait.
  - 期待結果: final top-level `human_gate`, `recommended_next_action == "address_review_feedback"`, not pass.
  - 失敗検出: wait ignores decision selected blocker or waits indefinitely after terminal evidence.
  - 検証方法: wait fake snapshot test.
  - 関連 closure id: `cli-002`

- `tc-s03-004` acceptance: fallback issue comment stays non-complete in wait
  - 前提: fake snapshot has fallback pass candidate, CI passed, no selected unresolved thread.
  - 操作: run wait until terminal gate.
  - 期待結果: `human_gate`, `wait_or_resume`, `observation_complete is false`, candidate remains visible.
  - 失敗検出: wait converts fallback candidate to pass/complete.
  - 検証方法: wait fake snapshot test.
  - 関連 closure id: `cli-003`, `cli-004`

Step closure contract:

- Close when wait semantic fingerprint, final payload, and progress use decision-scoped data, targeted tests pass, and per-step code review passes.

Report evidence destination:

- `report.md` session log, TDD evidence, Step Contract Closure rows for `cli-001`, `cli-002`, `cli-003`, `cli-004`, `cli-005`, Test Contract Closure, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate.

### S04 behavior slice: shipped skill output semantics

Behavior goal:

- Update `github-pr-observation/SKILL.md` so users and downstream agents know that final decision is current-boundary scoped, audit context is non-authoritative, fallback issue comments are low-confidence/non-promoting, and wait progress is decision-scoped/non-authoritative.

Planned contract:

- Scope:
  - Allowed: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - Tests: `tests/unit/infra/test_init_update.py` only if existing install-root asset content tests require an assertion update; otherwise inspect-only plus targeted pytest for asset inventory.
- Test obligation:
  - Cover AC-006, plus docs alignment for S01-S03 output fields.
- Red or alternative evidence requirement:
  - `inspect-only` is acceptable for prose. If adding structural content assertions is cheap and matches existing patterns, add them.
- Green verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "github_pr_observation or install_root or skill"`
  - Manual inspection that `SKILL.md` states authoritative `decision`, `review.current`, `review.audit`, `fallback_pass_candidate`, `decision_fingerprint`, and `audit_fingerprint` semantics.
- Refactor guardrail:
  - Do not change script public entrypoint or permission boundaries beyond documenting existing/implemented semantics.
- Amendment trigger:
  - If docs need to define broader fallback pass policy than Option C, stop for requirement/design update.

Delegation contract:

- delegated role: `doc-writer`
- input docs:
  - approved requirement/design/plan, S01-S03 final behavior evidence, target `SKILL.md`.
- allowed changes:
  - `SKILL.md` and, only if necessary, focused content/inventory tests.
- forbidden changes:
  - scripts, canonical docs, unrelated skills/docs.
- acceptance criteria:
  - Docs clearly distinguish final decision, current review evidence, audit history, fallback issue comment low confidence, and fingerprint purpose.
- required verification:
  - docs inspection and targeted pytest command if tests are changed.
- reviewer focus:
  - per-step `spec-reviewer` docs/spec alignment; if tests are changed, code-reviewer may be added for test-only diff.
- stop conditions:
  - Implemented behavior from S01-S03 differs from approved design or needs unapproved semantics.
- output required:
  - changed files, docs summary, verification/inspection result, unresolved risk, ledger note.

#### 具体テストケース一覧

- `tc-s04-001` inspect-only: output boundary semantics documented
  - 前提: S01-S03 behavior is implemented.
  - 操作: inspect `SKILL.md`.
  - 期待結果: `decision` is named as final decision-facing authority; `review.audit` / all-fetched legacy fields are documented as audit-only.
  - 失敗検出: docs still imply mixed `review.threads.unresolved` can be read as final blocker.
  - 検証方法: manual docs inspection and optional string assertion in `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: `cli-006`

- `tc-s04-002` inspect-only: fallback and fingerprint semantics documented
  - 前提: S01-S03 behavior is implemented.
  - 操作: inspect `SKILL.md`.
  - 期待結果: `fallback_issue_comment` remains top-level human gate/wait, `fallback_pass_candidate` is non-promoting, wait stability uses `decision_fingerprint`, and `audit_fingerprint` is debug-only.
  - 失敗検出: docs imply fallback candidate is merge-ready or audit fingerprint controls wait stability.
  - 検証方法: manual docs inspection and optional string assertion.
  - 関連 closure id: `cli-006`

Step closure contract:

- Close when docs match implemented behavior, docs/spec reviewer passes, and any changed tests pass.

Report evidence destination:

- `report.md` Docs Impact / docs refresh evidence, Step Contract Closure for `cli-006`, Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.

### S90 docs impact resolution / docs refresh

Behavior goal:

- Confirm whether docs beyond `SKILL.md` need updates. Based on current design, expected docs impact is `SKILL.md` only unless tests or public output semantics reveal another shipped doc reference.

Delegation contract:

- delegated role: `doc-writer` if docs beyond `SKILL.md` are needed; otherwise orchestrator records approved-no-op with inspection evidence.
- allowed paths:
  - Candidate only if needed: `src/spec_dock/assets/spec_dock/docs/...` or relevant shipped docs.
- forbidden changes:
  - canonical issue docs by delegated worker, implementation scripts, tests.
- required verification:
  - docs impact inspection, targeted docs/spec review.
- reviewer focus:
  - `spec-reviewer`.

Closure contract:

- Close with either docs update evidence or approved-no-op evidence that README/workflow/template docs do not require changes for this issue.

Report evidence destination:

- Docs Impact section, Reviewer Gate Status, Step Commit Gate or approved-no-op record.

### S99 final quality gate

Behavior goal:

- Validate the issue-wide outcome after all behavior/docs steps.

Required gates:

- QA gate:
  - `qa-reviewer` checks test sufficiency for AC-001 through AC-006 and EC-001 through EC-004.
  - Expected verification commands:
    - `uv run pytest tests/unit/infra/test_init_update.py`
    - `uv run pytest tests/unit`
    - Broaden to `uv run pytest` if shared install/update or runtime behavior is touched beyond the planned files.
- Issue-wide code review:
  - `code-reviewer` reviews integrated script/test diff across S01-S03 and any test changes in S04.
- Final spec review:
  - `spec-reviewer` verifies `requirement.md`, `design.md`, canonical `plan.md`, `report.md`, implementation, tests, and docs alignment.
- SpecDock validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync` if canonical docs/report were updated by orchestrator during adoption/execution.

Closure contract:

- Close only when all required closure ids are recorded as pass or approved-no-op in `report.md`, all implementation steps are committed or approved-no-op, docs impact is resolved, final QA/code/spec reviews pass, and final report ledger is complete.

Report evidence destination:

- Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Closure Coverage, Closure Delta, Final Commit / external delivery evidence.

## 6. Test Strategy Mapping

Test placement proposal:

- Keep primary regression coverage in `tests/unit/infra/test_init_update.py` because existing PR observation script tests already use fake `gh`, subprocess execution, temp script copies, and JSON assertions.
- Prefer extending existing helper families:
  - review collector: tests around `test_issue_176_s03_*` and `test_issue_75_pr_observation_review_collector_*`.
  - snapshot: tests around `test_issue_170_pr_observation_snapshot_*` and `fetch_pr_observation_snapshot.sh` cases.
  - wait: tests around `_issue_174_run_wait_fake_snapshots`, `test_issue_75_pr_observation_wait_*`, and `test_issue_170_pr_observation_wait_*`.
- Add focused assertions instead of a new test framework unless the file becomes unmanageable.

Risk-calibrated verification:

- S01 and S02 require red-first public-output tests because they change machine-readable contract.
- S03 requires red-first wait-loop test because the bug class is stability/progress contamination.
- S04 can be inspect-only unless existing asset tests have a clear structural assertion pattern worth extending.

## 7. Review Gates

Per-step gates:

- S01: `code-reviewer` after collector diff and tests pass.
- S02: `code-reviewer` after snapshot diff and tests pass.
- S03: `code-reviewer` after wait diff and tests pass.
- S04: `spec-reviewer` docs/spec alignment; add `code-reviewer` only if tests are changed materially.
- S90: `spec-reviewer` docs impact resolution.
- S99: final `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.

Reviewer pass must be fresh. Worker delegation is not a substitute for reviewer pass.

## 8. Rollback / Compatibility

Rollback:

- Each implementation step is a single review scope / commit, so rollback can revert the affected step commit.
- S01 rollback removes new output surfaces/fingerprint split; S02/S03 should be reverted first if they depend on S01 fields.
- S04 rollback only affects docs semantics.

Compatibility:

- Prefer additive migration.
- Keep legacy `review.threads`, `review.signals`, and `review.codex_authored` available.
- Add scope metadata such as `scope: "all_fetched"` and `decision_authoritative: false`, or sibling metadata if shape changes would be breaking.
- Keep existing status/action vocabulary except adding approved `status_reason` values from design.
- Do not promote `fallback_issue_comment` to pass in this issue.

## 9. Docs Impact

Required:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - Output Boundary: final JSON authority, decision/current/audit surface semantics.
  - Observation Semantics: current trigger / resume boundary is final-decision scope.
  - Fallback semantics: issue comments are low-confidence fallback; no-major-issues comments are `fallback_pass_candidate`, not pass.
  - Fingerprints: `decision_fingerprint` controls wait stability; `audit_fingerprint` is debug-only.

Likely not required unless implementation reveals references:

- Workflow docs and templates. The issue changes a shipped skill output contract, not SpecDock workflow lifecycle.

## 10. Final Quality Gate

Final exit proposal:

- All required closure ids in the Spec-Locked Closure Index have pass or approved-no-op evidence.
- Targeted tests pass:
  - `uv run pytest tests/unit/infra/test_init_update.py`
- Broader local suite passes or failures are classified as unrelated with evidence:
  - `uv run pytest tests/unit`
- `SKILL.md` docs semantics align with requirement/design/implementation.
- `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` all pass.
- `report.md` records implementation delegation, worker evidence, reviewer gates, closure coverage, docs impact, final gates, and commit/no-op evidence.
- No implementation readiness or issue completion is claimed until canonical orchestrator integrates this draft and completes required gates.

## 11. Plan Blockers

none.

Clarification candidates:

- none at plan time. Option C for `fallback_issue_comment` is already answered and adopted.

Implementation watchpoints:

- If legacy `review.codex_authored` cannot be scope-marked without changing list shape, prefer sibling metadata and record compatibility rationale in `report.md`.
- If no-major-issues phrase matching becomes broader than a narrow whitelist, stop and promote a design/requirement clarification.
- If `top-level fingerprint` compatibility conflicts with decision fingerprint semantics, keep explicit `decision_fingerprint` authoritative for wait and document any alias/transition choice in `report.md`.

## 12. Integration Notes for Main Orchestrator

Suggested adoption path:

- Record this draft in `report.md` Delegated Draft Evidence and Evidence Adoption Ledger if adopted.
- Integrate selected content into canonical `plan.md` only after orchestrator review.
- Keep canonical `plan.md` as the planned executable workflow contract; keep this draft as proposal evidence.
- Run fresh `spec-reviewer` on canonical `plan.md` after integration.

Lightweight provenance:

- created_by_role: `implementation-planner`
- scope_id: `iss-00182`
- source requirement revision: `spec-dock/active/issue/requirement.md`, status `approved`, 最終更新 `2026-06-12`
- source design revision: `spec-dock/active/issue/design.md`, status `approved`, 最終更新 `2026-06-12`
- source report revision: `spec-dock/active/issue/report.md`, current scaffold/evidence ledger state inspected
- leaf evidence used:
  - `20260612t012333z-research-pr-observation-final-output-boundary-analysis.md`
  - `20260612t014627z-interview-fallback-issue-comment-decision-boundary.md`
  - `20260612t015200z-draft-design-pr-observation-boundary.md`
  - `phase_plan_issue.md`
  - `authoring/issue-plan.md`
  - `workflow_issue.md`
  - provider-side `github-pr-observation` scripts / `SKILL.md`
  - `tests/unit/infra/test_init_update.py` existing PR observation test locations
- forbidden actions avoided:
  - no canonical docs edited
  - no implementation files edited
  - no tests edited
  - no config / `.agents` / `.codex` / `.github` edited
  - no GitHub state mutation
  - no git add / commit / push
- unresolved design gaps:
  - none

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
