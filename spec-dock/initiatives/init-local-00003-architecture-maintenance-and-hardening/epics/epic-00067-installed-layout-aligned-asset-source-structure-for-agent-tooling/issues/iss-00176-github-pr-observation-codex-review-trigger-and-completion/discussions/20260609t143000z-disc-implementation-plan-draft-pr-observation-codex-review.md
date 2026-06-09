---
created_by_role: implementation-planner
scope_id: iss-00176
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/active/epic/design.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
---

# iss-00176 implementation plan draft: GitHub PR observation Codex review trigger and completion

This is an evidence-only implementation-planning draft. It proposes a step order and closure coverage for `iss-00176`; it does not modify canonical artifacts and does not make approval, completion, or execution-go-ahead claims.

## Evidence Basis

- `requirement.md` requires default `post-once` trigger posting, explicit `resume`, fixed write boundary, final stdout JSON authority, selected review body full text in stdout, separate CI/review lifecycle, stale head fail-closed behavior, and timeout resume metadata.
- `design.md` fixes implementation order as fixed trigger write helper, wait trigger mode orchestration, snapshot/review JSON contract, then skill docs/package/tests. It also states that selected review bodies are not controlled by `body-mode`.
- `epic-00067` fixes agent-tooling asset authority under `src/spec_dock/assets/install_root/`.
- Current implementation evidence shows `wait_pr_observation.sh` accepts trigger metadata but does not post `@codex review`; `SKILL.md` still describes read-only scripts; `fetch_pr_review_snapshot.sh` has trigger inference/body-mode behavior that must be narrowed for normal wait/resume.
- `phase_plan_issue.md`, `authoring/issue-plan.md`, and `workflow_issue.md` require behavior-sliced steps, step-local delegation contracts, concrete test seeds, S90 docs impact resolution, S99 final quality gate, and report-ledger evidence.

## Proposed Step Dependency Order

1. S01 fixed trigger write helper.
2. S02 wait trigger mode orchestration.
3. S03 observation snapshot and review JSON contract.
4. S04 final stdout/out/status integration across wait polling.
5. S05 skill docs and shipped asset/package regression coverage.
6. S90 docs impact resolution.
7. S99 final quality gate.

Dependency rationale:

- S01 creates the only allowed write boundary used by S02.
- S02 owns public wait invocation modes and must pass explicit trigger metadata to S03.
- S03 owns selected review body, submitted PR review primary signal, collection summaries, and `body-mode` non-application to selected bodies.
- S04 integrates S01-S03 into one authoritative wait result, including timeout/resume, stale head, CI/review final status, stderr, and `--out`.
- S05 aligns user-facing skill contract and install/package regressions after behavior is stable.

## Proposed Spec-Locked Closure Index

| Closure ID | Step | Spec Link | Type | Locked Expectation | Observable Input / State | Bug Class Guarded | Required | Evidence Level | Closure Evidence |
|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | AC-001, AC-002, EC-005 | acceptance | fixed helper posts exactly one `@codex review` issue comment after pre-head match and returns comment metadata JSON | fake `gh` call log for helper or default wait path | missing trigger, wrong endpoint, existing trigger reuse | yes | red-required | helper test plus call log |
| cl-002 | S01 | AC-006 | negative | pre-trigger head mismatch does not POST and returns stale/non-success JSON | fake PR head mismatch before POST | stale PR accidentally triggers Codex review | yes | red-required | helper stale test |
| cl-003 | S01 | AC-007, EC-001 | negative | POST failure does not blind retry; only exact one-comment recovery is accepted | fake POST timeout plus before/after comments | duplicate trigger or unsafe recovery | yes | red-required | helper failure/recovery tests |
| cl-004 | S02 | AC-001, AC-008, EC-005, EC-007 | acceptance | wait default is `post-once`; `resume` requires explicit trigger metadata and never invokes trigger helper | `wait_pr_observation.sh` mode invocations | implicit no-post, auto reuse, double trigger | yes | red-required | wait usage/mode tests |
| cl-005 | S02 | AC-003 | invariant | trigger helper stdout is captured internally and user-facing stdout remains one final JSON | wait with helper JSON and snapshot polling | mixed stdout JSON stream | yes | red-required | stdout parse test |
| cl-006 | S03 | AC-004, EC-002 | acceptance | Codex-authored submitted PR review is primary completion signal; fallback remains low-confidence/human-gate or timeout | fake reviews/comments after trigger | quiet-window or issue-comment primary completion | yes | red-required | review lifecycle tests |
| cl-007 | S03 | AC-003, AC-004, EC-006 | invariant | selected PR review and selected review comment bodies appear in final stdout JSON as full text regardless of `body-mode` | `--body-mode none`, `out-only`, `trigger-window-truncated` | body hidden in `--out`, truncated selected body, extra API dependency | yes | red-required | body-mode regression tests |
| cl-008 | S03 | AC-008, EC-007 | acceptance | reviews, review comments, and review threads expose fetched IDs, selected IDs, boundary-before exclusion evidence; threads expose unresolved IDs/counts | resume run with trigger-before and trigger-after artifacts | timeout/resume collection gap | yes | red-required | collection summary tests |
| cl-009 | S04 | AC-005, EC-003, EC-004 | acceptance | CI and review lifecycle are independent and final status/recommended action distinguishes mixed states | CI failed/review completed; CI passed/review pending | success from one completed family only | yes | red-required | wait final status tests |
| cl-010 | S04 | AC-006 | negative | post-trigger and polling head mismatch preserve trigger metadata but return stale/non-success and do not delete comments | fake current head drift after POST or during poll | stale head marked success, cleanup mutation | yes | red-required | stale wait tests |
| cl-011 | S04 | AC-003, EC-006 | invariant | stdout is authoritative final JSON, stderr is bounded progress/diagnostics, `--out/result.json` equals stdout, `summary.md` is absent | wait with `--out` and progress modes | authority split or stale summary artifact | yes | red-required | stdout/stderr/out tests |
| cl-012 | S04 | AC-008, EC-007 | acceptance | timeout/limit payload includes resume metadata and command hint for same boundary | timeout before review or CI completion | unresumable timeout | yes | red-required | timeout resume test |
| cl-013 | S05 | Scope, constraints, epic design | scaffold/package | `trigger_codex_review.sh` and updated skill assets are included in source install root, init/update layout, and package inventory | install/update/package regression tests | source/dogfooding/package drift | yes | red-required | package/install tests |
| cl-014 | S05 | Scope, non-scope, constraints | docs/spec | `SKILL.md` describes fixed trigger write plus read-only observation; retired `pr-monitor` and retired review-comments skill stay retired | docs inspection and existing removal tests | old workflow revival or user-side trigger discretion | yes | inspect-only | docs/spec review |
| cl-015 | S90 | docs impact | docs/spec | required docs/skill/package text impact is resolved or explicitly no-op with evidence | changed docs/templates/skill surfaces | undocumented breaking contract | yes | inspect-only | S90 report evidence |
| cl-016 | S99 | workflow issue final gate | quality | QA, issue-wide code review, final spec review, final validation, and final diff/report gates are recorded as future required gates | full issue diff and test evidence | step-local pass masking integrated failure | yes | manual-required | S99 gate evidence |

## Proposed Requirements To Step Mapping

- AC-001 -> S01, S02
- AC-002 -> S01
- AC-003 -> S02, S03, S04
- AC-004 -> S03
- AC-005 -> S04
- AC-006 -> S01, S04
- AC-007 -> S01
- AC-008 -> S02, S03, S04
- EC-001 -> S01
- EC-002 -> S03
- EC-003 -> S04
- EC-004 -> S04
- EC-005 -> S01, S02
- EC-006 -> S03, S04
- EC-007 -> S02, S03, S04
- Non-negotiable constraints -> S01, S02, S03, S04, S05
- Out of scope / retired workflow constraints -> S05, S90

## Implementation Step S01: fixed trigger write helper

- Behavior goal:
  - Add a fixed write helper that posts only the exact `@codex review` PR issue comment when the expected head SHA still matches, and returns machine-readable trigger JSON.
- Dependencies:
  - `requirement.md` AC-001, AC-002, AC-006, AC-007.
  - `design.md` `trigger_codex_review.sh` interface contract.
- Unblocks:
  - S02 wait `post-once` orchestration.
  - S04 wait stale/failure integration.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- Closure ids:
  - `cl-001`, `cl-002`, `cl-003`
- Planned contract:
  - Scope:
    - Add the helper script and tests for fixed endpoint, fixed body, strict validation, pre/post head checks, POST failure, and exact one-comment recovery.
  - Delegation contract:
    - Delegated role: `dev-coder`.
    - Input docs: requirement, design, current scripts, tests.
    - Allowed paths: the helper script and focused tests only.
    - Forbidden changes: wait orchestration, snapshot/review collector behavior, skill docs, GitHub state, secrets.
    - Required verification: focused pytest selection for helper script contract; call-log inspection from fake `gh`.
    - Stop conditions: helper needs caller-provided body/endpoint, non-fixed GitHub mutation, or cannot distinguish recovery ambiguity.
    - Output required: changed files, test results, fake `gh` write call log summary, Ledger Note or no material decision note.
  - Concrete test case seeds:
    - `tc-s01-001` acceptance: helper posts fixed issue comment
      - 前提: fake `gh pr view` returns matching `headRefOid`.
      - 操作: `trigger_codex_review.sh --repo owner/repo --pr 13 --head-sha abc1234`.
      - 期待結果: one `gh api --method POST repos/owner/repo/issues/13/comments -f body=@codex review`-equivalent call and JSON with comment id/created_at/body evidence.
      - 失敗検出: wrong endpoint, missing POST, caller-controlled body, or multiple POST calls.
      - 検証方法: `tests/unit/infra/test_init_update.py` fake `gh` contract test.
      - 関連 closure id: `cl-001`
    - `tc-s01-002` negative: pre-trigger stale head does not post
      - 前提: fake initial PR head differs from `--head-sha`.
      - 操作: helper invocation with old SHA.
      - 期待結果: no POST call; stdout JSON reports stale/non-success with current head evidence.
      - 失敗検出: stale PR triggers Codex review.
      - 検証方法: focused fake `gh` call-log assertion.
      - 関連 closure id: `cl-002`
    - `tc-s01-003` negative: POST failure fail-closed
      - 前提: fake POST returns timeout/error and after snapshot yields zero or multiple exact-body candidates.
      - 操作: helper invocation.
      - 期待結果: no blind retry; final JSON carries blocking limitation.
      - 失敗検出: second POST or ambiguous recovery accepted.
      - 検証方法: fake `gh` call-count and JSON limitation assertions.
      - 関連 closure id: `cl-003`
    - `tc-s01-004` recovery: exactly one new comment can be recovered
      - 前提: fake POST response is lost but before/after issue comments show exactly one new exact `@codex review` comment.
      - 操作: helper invocation.
      - 期待結果: JSON action is recovered, with recovered comment metadata and no second POST.
      - 失敗検出: recovery ignored or recovered without exact-one proof.
      - 検証方法: fake before/after comments fixture.
      - 関連 closure id: `cl-003`
- Step closure contract:
  - Close when all required S01 tests pass, helper executable permissions are correct, and no non-fixed write surface is exposed.
  - Report evidence destination: `report.md` Implementation Delegation Gate, TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage.
- Step gate:
  - Reviewer: `code-reviewer`.
  - Scope: helper script, tests, fixed write boundary, failure recovery.
  - Commit boundary: S01 only.

## Implementation Step S02: wait trigger mode orchestration

- Behavior goal:
  - Make `wait_pr_observation.sh` default to `post-once`, add explicit `resume`, and ensure trigger metadata is passed through without leaking helper stdout.
- Dependencies:
  - S01.
  - Existing wait parser/polling behavior.
- Unblocks:
  - S03 explicit boundary collection.
  - S04 final wait status integration.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- Closure ids:
  - `cl-004`, `cl-005`
- Planned contract:
  - Scope:
    - Add `--trigger-mode post-once|resume`; default to `post-once`; reject metadata in `post-once`; require both metadata fields in `resume`; call S01 helper exactly once in `post-once`; never call it in `resume`.
  - Delegation contract:
    - Delegated role: `dev-coder`.
    - Allowed paths: wait script and focused tests.
    - Forbidden changes: review selection JSON implementation beyond passing explicit metadata; skill docs; package inventory.
    - Required verification: usage validation tests, stdout parse tests, fake helper/snapshot call flow.
    - Stop conditions: implicit trigger reuse is needed, `post-once` cannot prevent metadata ambiguity, or helper stdout cannot be captured.
    - Output required: changed files, test results, call flow evidence, Ledger Note or no material decision note.
  - Concrete test case seeds:
    - `tc-s02-001` acceptance: default wait posts once before polling
      - 前提: fake helper succeeds and fake snapshot reaches terminal status.
      - 操作: `wait_pr_observation.sh --repo owner/repo --pr 13 --head-sha abc1234`.
      - 期待結果: helper is called once before snapshot; snapshot receives helper `comment_id` and `created_at`.
      - 失敗検出: no helper call, repeated helper call, or inferred trigger used.
      - 検証方法: fake helper/snapshot call log.
      - 関連 closure id: `cl-004`
    - `tc-s02-002` negative: resume does not post
      - 前提: explicit trigger id/time are supplied.
      - 操作: wait with `--trigger-mode resume --trigger-comment-id 456 --trigger-created-at 2026-06-09T10:00:00Z`.
      - 期待結果: no helper/POST call; snapshot receives explicit metadata.
      - 失敗検出: resume posts a new trigger or drops boundary metadata.
      - 検証方法: fake call log.
      - 関連 closure id: `cl-004`
    - `tc-s02-003` negative: invalid mode/metadata combinations fail usage
      - 前提: `post-once` with trigger metadata, or `resume` missing one metadata field.
      - 操作: invalid wait invocation.
      - 期待結果: usage error before any `gh`, helper, or snapshot command.
      - 失敗検出: ambiguous mode accepted.
      - 検証方法: exit code and empty fake call log.
      - 関連 closure id: `cl-004`
    - `tc-s02-004` invariant: helper stdout does not leak
      - 前提: helper returns JSON and snapshot returns terminal JSON.
      - 操作: default wait invocation.
      - 期待結果: stdout parses as one JSON final result only; helper JSON is integrated, not emitted separately.
      - 失敗検出: two JSON documents on stdout.
      - 検証方法: stdout parse and document-count assertion.
      - 関連 closure id: `cl-005`
- Step closure contract:
  - Close when mode validation, helper orchestration, explicit boundary forwarding, and stdout capture are covered.
  - Report evidence destination: report TDD evidence, Implementation Delegation Gate, Step/Test Closure, Closure Coverage.
- Step gate:
  - Reviewer: `code-reviewer`.
  - Scope: wait CLI contract, usage validation, helper integration, stdout boundary.
  - Commit boundary: S02 only.

## Implementation Step S03: snapshot and review JSON contract

- Behavior goal:
  - Make read-only snapshot/review collectors expose explicit trigger boundary, submitted PR review lifecycle, selected full bodies, and collection summaries needed by wait/resume.
- Dependencies:
  - S02 trigger metadata forwarding.
- Unblocks:
  - S04 final status and authoritative output.
  - S05 docs/package contract.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh` only if minimal CI integration evidence requires it.
  - `tests/unit/infra/test_init_update.py`
- Closure ids:
  - `cl-006`, `cl-007`, `cl-008`
- Planned contract:
  - Scope:
    - Prefer explicit trigger metadata over inference for normal wait/resume; keep direct diagnostic inference only with limitations. Add `codex_review.lifecycle`, selected reviews/comments full bodies, collection summaries, unresolved thread IDs/counts, and selected body collection status.
  - Test obligation:
    - `body-mode` must not apply to selected body full text: `body-mode none`, `out-only`, and `trigger-window-truncated` must still leave selected review/comment body in stdout JSON.
  - Delegation contract:
    - Delegated role: `dev-coder`.
    - Allowed paths: snapshot/review collector scripts and focused tests.
    - Forbidden changes: write helper behavior, wait mode parser, skill docs.
    - Required verification: fake issue comments, PR reviews, review comments, reviewThreads GraphQL fixtures; stdout JSON assertions.
    - Stop conditions: selected body cannot be collected without unsafe follow-up GitHub API, or Codex author heuristic changes require a design decision.
    - Output required: changed files, verification result, JSON schema examples, Ledger Note or no material decision note.
  - Concrete test case seeds:
    - `tc-s03-001` acceptance: submitted PR review is primary completion
      - 前提: trigger after timestamp exists and fake Codex-authored submitted PR review is after boundary.
      - 操作: snapshot/review collector invocation with explicit trigger metadata.
      - 期待結果: `codex_review.lifecycle.completion_signal=submitted_pull_request_review`, high confidence, selected review id present.
      - 失敗検出: issue comment, reaction, or quiet window marked primary.
      - 検証方法: fake GitHub JSON fixture test.
      - 関連 closure id: `cl-006`
    - `tc-s03-002` negative: fallback activity is not primary
      - 前提: only Codex issue comment/reaction/quiet window signal exists.
      - 操作: collector invocation.
      - 期待結果: fallback/timeout/human_gate with limitation or lower confidence, not primary submitted review completion.
      - 失敗検出: non-review object selected as primary completion.
      - 検証方法: fake fixture assertion.
      - 関連 closure id: `cl-006`
    - `tc-s03-003` invariant: selected bodies ignore body-mode
      - 前提: selected Codex PR review and selected review comment have long body text.
      - 操作: collector or wait path with `--body-mode none`, `out-only`, and `trigger-window-truncated`.
      - 期待結果: `codex_review.selected_reviews[].body` and `selected_review_comments[].body` contain full selected text in stdout JSON for each mode.
      - 失敗検出: selected body omitted, truncated, or only written under `--out`.
      - 検証方法: parametrized fake fixture test.
      - 関連 closure id: `cl-007`
    - `tc-s03-004` negative: selected body collection failure is non-success/human-gate
      - 前提: selected review metadata exists but body is unavailable.
      - 操作: collector invocation.
      - 期待結果: item has `body_collection_status` and limitation; success is not claimed.
      - 失敗検出: empty body with success.
      - 検証方法: fake malformed/partial fixture test.
      - 関連 closure id: `cl-007`
    - `tc-s03-005` acceptance: resume collection summary covers all families
      - 前提: before-boundary and after-boundary reviews/comments/threads exist; one thread unresolved.
      - 操作: collector with explicit trigger metadata.
      - 期待結果: fetched IDs, selected IDs, boundary-before excluded IDs/reasons, unresolved IDs/counts are present.
      - 失敗検出: timeout/resume gap cannot be audited.
      - 検証方法: fake paginated REST and GraphQL fixture test.
      - 関連 closure id: `cl-008`
- Step closure contract:
  - Close when explicit boundary selection, primary completion, selected body full text, collection summary, and fallback limitations are covered.
  - Report evidence destination: report TDD evidence, Step/Test Closure, Closure Coverage, any material heuristic decision in Decision Ledger.
- Step gate:
  - Reviewer: `code-reviewer`.
  - Scope: read-only collector JSON contract and tests.
  - Commit boundary: S03 only.

## Implementation Step S04: wait final JSON, mixed status, timeout/resume, and output authority

- Behavior goal:
  - Integrate trigger, CI, review, head state, timeout/resume, stdout/stderr, and `--out` into one authoritative final wait JSON.
- Dependencies:
  - S01, S02, S03.
- Unblocks:
  - S05 public docs/package contract.
  - S99 final quality gate.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh` if final status fields must be surfaced there.
  - `tests/unit/infra/test_init_update.py`
- Closure ids:
  - `cl-009`, `cl-010`, `cl-011`, `cl-012`
- Planned contract:
  - Scope:
    - Classify CI and review independently, merge them into `overall_status`/`recommended_next_action`, fail stale head closed, preserve trigger metadata after post-trigger drift, write `resume` metadata on timeout, and keep output authority boundaries.
  - Delegation contract:
    - Delegated role: `dev-coder`.
    - Allowed paths: wait/snapshot final integration and focused tests.
    - Forbidden changes: new GitHub write surfaces, docs/package-only changes, relaxing selected body contract.
    - Required verification: mixed-state wait fixtures, stale-head phases, timeout/resume payload, `--out/result.json` equality, no `summary.md`.
    - Stop conditions: final status needs a new requirement-level state taxonomy, or review/CI precedence conflicts with AC/EC.
    - Output required: changed files, test output, representative final JSON excerpts, Ledger Note or no material decision note.
  - Concrete test case seeds:
    - `tc-s04-001` acceptance: CI failed with review completed is non-merge-ready
      - 前提: fake CI failed and Codex submitted review exists.
      - 操作: wait invocation.
      - 期待結果: review completion is recorded but `overall_status`/next action is failed or human-gate, not merge-ready success.
      - 失敗検出: review completion masks CI failure.
      - 検証方法: wait final JSON assertion.
      - 関連 closure id: `cl-009`
    - `tc-s04-002` acceptance: CI passed with review pending waits or times out as review pending
      - 前提: fake CI passed and no submitted Codex review exists before deadline.
      - 操作: wait invocation with short timeout.
      - 期待結果: timeout or pending review status with resume metadata; not passed.
      - 失敗検出: CI terminal alone marks success.
      - 検証方法: fake polling test.
      - 関連 closure id: `cl-009`, `cl-012`
    - `tc-s04-003` negative: post-trigger head drift is stale with trigger metadata
      - 前提: helper posts successfully, then current head differs.
      - 操作: wait invocation.
      - 期待結果: final JSON includes trigger id/time and stale/non-success head phase; no delete mutation occurs.
      - 失敗検出: stale head marked success or trigger metadata lost.
      - 検証方法: fake call log and final JSON assertion.
      - 関連 closure id: `cl-010`
    - `tc-s04-004` invariant: stdout/stderr/out authority
      - 前提: wait runs with `--out`.
      - 操作: wait invocation with progress mode variants.
      - 期待結果: stdout parses as one final JSON; stderr has bounded progress/diagnostics only; `--out/result.json` equals stdout; `summary.md` absent.
      - 失敗検出: authority split or generated summary.md.
      - 検証方法: filesystem and stream assertions.
      - 関連 closure id: `cl-011`
    - `tc-s04-005` acceptance: timeout exposes resume command hint
      - 前提: CI or review remains pending until timeout and trigger metadata exists.
      - 操作: default wait with short timeout.
      - 期待結果: `resume.available=true`, trigger id/time/head SHA present, command hint uses `--trigger-mode resume`.
      - 失敗検出: timeout cannot be resumed without external API exploration.
      - 検証方法: final JSON assertion.
      - 関連 closure id: `cl-012`
- Step closure contract:
  - Close when final wait JSON satisfies mixed status, stale, timeout/resume, selected body availability through stdout, stderr, and `--out` boundaries.
  - Report evidence destination: report TDD evidence, Step/Test Closure, Closure Coverage, discovered tests.
- Step gate:
  - Reviewer: `code-reviewer`.
  - Scope: integrated wait behavior and tests.
  - Commit boundary: S04 only.

## Implementation Step S05: skill docs and shipped asset/package regression coverage

- Behavior goal:
  - Align public skill documentation and shipped asset/package tests with the new fixed trigger write plus read-only observation contract.
- Dependencies:
  - S01-S04 behavior contracts are stable enough to document.
- Unblocks:
  - S90 docs impact resolution.
  - S99 final quality gate.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `tests/unit/infra/test_init_update.py`
  - Package/install inventory expectations for `trigger_codex_review.sh` within the same test file.
- Closure ids:
  - `cl-013`, `cl-014`
- Planned contract:
  - Scope:
    - Update `SKILL.md` entrypoints/options/semantics/safety boundary. Add install/package assertions that new helper is included. Preserve retired skill/sub-agent non-revival constraints.
  - Delegation contract:
    - Delegated role: `doc-writer` for skill text, with `dev-coder` for test/package assertions if split is preferable.
    - Allowed paths: `SKILL.md` and focused package/install tests.
    - Forbidden changes: implementation scripts except corrections required by reviewer findings from S01-S04; canonical docs; workflow docs unless S90 escalates.
    - Required verification: docs inspection plus focused pytest for installed asset inventory; no `pr-monitor`/retired skill revival.
    - Stop conditions: docs require behavior not implemented by S01-S04, or package test changes imply installer source authority outside `install_root`.
    - Output required: changed files, docs diff summary, test results, Ledger Note or no material decision note.
  - Concrete test case seeds:
    - `tc-s05-001` acceptance: helper script is installed and packaged
      - 前提: current install-root asset tree includes `trigger_codex_review.sh`.
      - 操作: existing init/update/package inventory tests run.
      - 期待結果: source, installed layout, wheel/sdist/package inventories include the helper.
      - 失敗検出: hidden asset added in source but absent from install/package.
      - 検証方法: focused pytest around install-root managed skill inventory.
      - 関連 closure id: `cl-013`
    - `tc-s05-002` inspect-only: skill docs state new contract
      - テスト不要理由: docs wording is a public contract artifact and should be checked by inspection/spec review, with structural assertions where already available.
      - 代替検証方法: inspect `SKILL.md` for default `post-once`, explicit `resume`, fixed `@codex review` write, stdout/stderr/out authority, selected body stdout, and retired workflow prohibition.
      - 期待結果: docs match requirement/design and do not claim arbitrary write automation.
      - 記録先: report S90/Delegated Worker Evidence.
      - 関連 closure id: `cl-014`
- Step closure contract:
  - Close when docs and package/install tests reflect the new contract and no retired workflow is restored.
  - Report evidence destination: report Delegated Worker Evidence, docs inspection evidence, Step/Test Closure, Closure Coverage.
- Step gate:
  - Reviewer: `spec-reviewer` for docs/spec alignment and `code-reviewer` for package/install test diff if both remain in one step; otherwise split this step before implementation.
  - Commit boundary: S05 only, or split into S05a docs and S05b package tests if reviewer scope would otherwise mix.

## S90 docs impact resolution / docs refresh

- Behavior goal:
  - Resolve documentation impact after implementation steps without expanding beyond issue scope.
- Dependencies:
  - S01-S05.
- Unblocks:
  - S99 final quality gate.
- Target files:
  - Primary expected docs target is `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`.
  - Additional docs/templates/workflow files only if implementation or review shows they are directly impacted.
- Closure ids:
  - `cl-015`
- Planned contract:
  - Scope:
    - Confirm whether docs/templates/README/workflow/skill/migration notes need updates. If only skill docs changed in S05, record that wider docs impact is resolved/no-op with evidence.
  - Delegation contract:
    - Delegated role: `doc-writer` if additional docs updates are required; otherwise N/A with inspect-only evidence.
    - Allowed paths: impacted docs only; do not touch canonical issue docs from this delegated step unless orchestrator later adopts separately.
    - Forbidden changes: implementation scripts/tests/config/GitHub state/secrets.
    - Required verification: docs diff inspection and `spec-reviewer` docs/spec alignment.
    - Stop conditions: docs impact requires new requirement/design decision or wider workflow policy change.
    - Output required: docs changed/no-op rationale, verification, unresolved docs risks.
  - Concrete test case seed:
    - `tc-s90-001` inspect-only: docs impact is resolved
      - テスト不要理由: docs impact is a review/inspection gate.
      - 代替検証方法: list docs surfaces checked and compare against requirement/design.
      - 期待結果: no required docs impact remains unrecorded; skill docs align with implemented contract.
      - 記録先: report S90 docs impact evidence and Final Spec Review Gate input.
      - 関連 closure id: `cl-015`
- Step closure contract:
  - Close when docs impact is either updated by doc-writer or explicitly no-op with evidence, then reviewed for docs/spec alignment.
- Step gate:
  - Reviewer: `spec-reviewer`.
  - Commit boundary: S90 docs-only commit or approved-no-op evidence.

## S99 final quality gate

- Behavior goal:
  - Confirm the issue-wide integrated result, closure coverage, and final evidence before any completion workflow.
- Dependencies:
  - S01-S05 and S90.
- Target files:
  - Full issue diff and report evidence; no new feature implementation unless a reviewer finding creates bounded follow-up work.
- Closure ids:
  - `cl-016`
- Planned contract:
  - Required validation candidates:
    - Focused pytest selections from `tests/unit/infra/test_init_update.py` covering the helper, wait mode, snapshot/review contract, output boundaries, and install/package inventory.
    - Broader relevant lane if focused tests indicate shared regression risk, likely `uv run pytest tests/unit/infra/test_init_update.py`.
    - `git diff --check`.
    - `git status --short`.
  - Final QA gate:
    - Delegated role: `qa-reviewer`.
    - Focus: AC/EC/constraint closure coverage, missing high-value tests, integration test necessity, `body-mode` selected-body obligation coverage.
  - Final code review gate:
    - Delegated role: `code-reviewer`.
    - Focus: integrated script/test/package diff, fixed write boundary, read-only collector boundary, failure modes, maintainability.
  - Final spec review gate:
    - Delegated role: `spec-reviewer`.
    - Focus: requirement/design/plan/report/docs/implementation/tests consistency.
  - Stop conditions:
    - Any final reviewer returns fail, required closure lacks evidence, unresolved Evidence Adoption Ledger entry remains, or tests fail due to issue changes.
  - Concrete test case seed:
    - `tc-s99-001` manual-required: final integrated gate
      - 前提: S01-S05 and S90 closure evidence exists.
      - 操作: run final validation and delegated final reviews.
      - 期待結果: QA, code, and spec reviews are all fresh passed in report evidence before completion claims.
      - 失敗検出: step-local pass hides missing integrated behavior or docs/test mismatch.
      - 検証方法: report gate evidence plus commands above.
      - 関連 closure id: `cl-016`
- Step closure contract:
  - Close only when report evidence records final QA/code/spec gates and validation results.
- Step gate:
  - Reviewer: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.
  - Commit boundary: final report/cleanup commit after gates, or bounded follow-up commits per reviewer findings.

## Proposed Final Exit Contract

- All required closure ids `cl-001` through `cl-016` have report evidence.
- Every implementation step is closed as committed or justified approved-no-op.
- `body-mode` selected-body non-application is covered by planned tests and report evidence.
- No GitHub state, secrets, arbitrary write surface, retired sub-agent, or retired skill compatibility shim is introduced.
- `report.md` records delegated worker evidence, reviewer gate status, closure coverage, docs impact, final validation, and final review outcomes before any completion claim.

## Diff Guard Note

- Final check command before finishing this draft:
  - `git status --short`
- Observed status:
  - Pre-existing modified canonical docs remained present:
    - `M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/design.md`
    - `M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/report.md`
    - `M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/requirement.md`
  - Pre-existing untracked discussion evidence remained present:
    - `?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/discussions/20260608t085332z-research-chatgpt55-pro-analysis-request-package.md`
    - `?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/discussions/20260608t092803z-research-chatgpt55-pro-codex-review-trigger-completion-analysis.md`
    - `?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/discussions/20260608t111111z-research-deterministic-codex-review-trigger-design.md`
    - `?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/discussions/20260609t030339z-interview-issue-scope-for-deterministic-codex-review-trigger.md`
    - `?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/discussions/20260609t130000z-interview-review-body-output-contract.md`
    - `?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/discussions/20260609t133000z-disc-design-draft-system-architect-pr-observation-codex-review.md`
  - This task added only the requested discussion draft:
    - `?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/discussions/20260609t143000z-disc-implementation-plan-draft-pr-observation-codex-review.md`
- Diff guard result:
  - pass for this delegated draft scope: no canonical docs, implementation files, tests, config, agent instructions, workflow files, GitHub state, or secrets were edited by this task.
