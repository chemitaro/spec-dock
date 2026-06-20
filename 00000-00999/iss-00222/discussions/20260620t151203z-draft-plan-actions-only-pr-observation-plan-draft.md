---
kind: draft-plan
created_by_role: implementation-planner
scope_id: iss-00222
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/discussions/20260620t143349z-adr-forbid-checks-api-in-pr-observation.md
  - spec-dock/active/issue/discussions/20260620t144016z-interview-checks-named-compatibility-boundary.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
intended_targets:
  - plan.md
  - report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# Actions Only Pr Observation Plan Draft

This is delegated planning evidence for `iss-00222`. It is not canonical `plan.md`, is not a reviewer pass, and does not claim phase promotion, implementation readiness, final authority, or completion ownership.

## 1. Plan Summary

- Goal: move `github-pr-observation` CI observation to GitHub Actions workflow runs/jobs only, while preserving PR metadata, review, comments, and review thread observation.
- Primary implementation source: provider-side shipped assets under `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` and runtime doctor code under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`.
- Forbidden CI surfaces: `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, `gh pr checks` equivalent, and limitations that treat missing Checks/statuses/rollup access as a defect.
- Compatibility boundary: `checks` named files or JSON fields may remain when needed, but they must be historical or deprecated compatibility metadata, not observed CI evidence.
- Execution style: one behavior slice per step; each implementation step is one review scope and one commit scope.
- Evidence destination: observed results belong in `report.md`, especially Implementation Delegation Gate, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, Final QA Gate, Final Code Review Gate, Final Spec Review Gate, and Evidence Adoption Ledger where delegated evidence is adopted.

## 2. Requirement / Design Traceability

- AC-001: S01 forbids Checks/status/rollup calls and adds fake-gh/static regression coverage.
- AC-002: S02 classifies successful Actions workflow runs/jobs as passed; S03 preserves wait/snapshot compatibility for passed state.
- AC-003: S02 classifies failed, pending, queued, running, cancelled, timed out, and unknown Actions states without fallback; S03 consumes those states in wait/progress/fingerprint logic.
- AC-004: S02 makes zero Actions runs non-pass; S03 ensures wait decisions do not recover pass from legacy fields.
- AC-005: S04 preserves review/comment/thread evidence while forbidden CI surfaces are blocked.
- AC-006: S05 migrates doctor/capability diagnostics away from Checks/statuses/rollup permission requirements.
- AC-007: S90 updates shipped skill/docs/template wording so API prohibition is not confused with a word ban.
- EC-001: S02 treats Actions API unavailable as unknown/human gate without fallback.
- EC-002: S02 keeps run-level failed when jobs API is unavailable.
- EC-003: S90 documents external/non-Actions checks as intentionally unobserved; S03 avoids claiming GitHub UI mergeability.
- EC-004: S02 treats status-only repositories as non-pass/unknown/human gate.
- EC-005: S01 and S90 allow compatibility names while forbidding GitHub Checks API use.
- Non-negotiable constraints: all implementation steps keep provider-side source of truth first, do not weaken review/comment observation, and do not edit dogfooding mirror as implementation source.

## 3. Milestones

- M1 CI source boundary locked:
  - S01 closes forbidden API regression guard.
  - S02 closes Actions-only CI classification.
- M2 Downstream observation consumers synchronized:
  - S03 closes snapshot/wait compatibility and progress/fingerprint behavior.
  - S04 closes review/comment/thread preservation.
- M3 Runtime diagnostics and guidance synchronized:
  - S05 closes doctor/capability migration.
  - S90 closes docs, skill wording, merge-preparer wording, and compatibility naming guidance.
- M4 Final evidence and quality gates:
  - S99 closes issue-wide QA, code review, spec review, final validation, and report evidence requirements.

## 4. Dependency-Derived Execution Order

Design dependency source:

1. `pr_observation_checks.py` owns CI collection and classification. It must be fixed before downstream snapshot/wait behavior can be trusted.
2. `pr_observation_snapshot.py` and `pr_observation_wait.py` consume CI payload. They should change after the collector exposes Actions-only payload semantics.
3. `pr_review_snapshot.py` is a parallel review/comment collector. It should be regression-checked after CI forbidden surfaces are blocked.
4. `github_capability_cli.py` and `doctor.py` consume the new capability model. They should change after the Actions-only CI contract is known.
5. Skill/docs/template wording should be updated after implementation semantics and capability behavior are fixed.
6. S99 runs only after all step-local review/commit gates and S90 docs impact resolution are complete.

Step dependency summary:

- S01 depends on approved requirement/design and accepted ADR; unblocks all runtime CI changes.
- S02 depends on S01 guard coverage; unblocks S03 wait/snapshot consumer changes.
- S03 depends on S02 payload semantics; unblocks S99 integration assessment and S90 merge-preparer wording.
- S04 depends on S01 guard coverage; can run after S02 or in a separate review scope once forbidden calls fail fast.
- S05 depends on S02 source policy; unblocks S90 diagnostic wording.
- S90 depends on S02, S03, and S05 semantics.
- S99 depends on S01-S05 and S90 committed or approved-no-op closure.

## 5. Issue / Step Slicing

### Step List

- S01 Forbidden CI surface guard and collector boundary
  - Behavior: PR observation CI collection does not call forbidden Checks/status/rollup surfaces.
  - Depends on: requirement/design/ADR.
  - Unblocks: S02, S03, S04.
  - Target files: `pr_observation_checks.py`, `tests/unit/infra/test_init_update.py`, focused fake-gh fixtures.
  - Review gate: `code-reviewer`.

- S02 Actions-only CI state classification
  - Behavior: Actions workflow runs/jobs alone determine pass/fail/pending/running/unknown/none.
  - Depends on: S01.
  - Unblocks: S03, S05, S90.
  - Target files: `pr_observation_checks.py`, `tests/unit/infra/test_init_update.py`.
  - Review gate: `code-reviewer`.

- S03 Snapshot/wait compatibility and decision consumption
  - Behavior: snapshot/wait/progress/fingerprint consume Actions summary and legacy compatibility fields are not decision evidence.
  - Depends on: S02.
  - Unblocks: S90, S99.
  - Target files: `pr_observation_snapshot.py`, `pr_observation_wait.py`, relevant shell entrypoint usage text only if needed, focused tests.
  - Review gate: `code-reviewer`.

- S04 Review/comment/thread preservation regression
  - Behavior: review/comment/thread evidence remains collected while forbidden CI endpoints are blocked.
  - Depends on: S01.
  - Unblocks: S99.
  - Target files: `pr_review_snapshot.py` inspection if needed, tests around observation snapshot/review payload.
  - Review gate: `code-reviewer`.

- S05 Doctor/capability migration
  - Behavior: PR observation diagnostics require Actions and review/comment read capability, not Checks/statuses/status rollup capability.
  - Depends on: S02.
  - Unblocks: S90, S99.
  - Target files: `github_capability_cli.py`, `doctor.py`, `tests/cli_runtime/test_runtime_doctor_s04.py`.
  - Review gate: `code-reviewer`.

- S90 Docs impact resolution and skill wording
  - Behavior: shipped skill/docs/template guidance states Actions-only observation, intentional losses, and compatibility naming boundary.
  - Depends on: S02, S03, S05.
  - Unblocks: S99.
  - Target files: shipped skill/docs/templates listed in design.
  - Review gate: `spec-reviewer`.

- S99 Final quality gate
  - Behavior: issue-wide evidence, tests, docs, reviews, and closure ledgers are complete.
  - Depends on: S01-S05, S90.
  - Target files: `report.md` only for evidence integration by main orchestrator, plus no product mutation unless prior reviewer asks for amendment.
  - Review gate: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.

### Spec-Locked Closure Index

| ID | Step | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | acceptance | AC-001 | CI collector never calls `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, or `gh pr checks` equivalent | fake `gh` configured to fail on forbidden surfaces | forbidden fallback regression | yes | red-required | Test Contract Closure + fake-gh call log |
| cl-002 | S02 | acceptance | AC-002 | Actions success terminal state can produce passed CI without Checks/status limitation | workflow runs/jobs fixture for current head SHA | loss of valid Actions pass | yes | red-required | Test Contract Closure + JSON payload |
| cl-003 | S02 | acceptance | AC-003 | Actions failure/pending/running states classify from Actions only | workflow run/job fixtures for each state family | mixed-source or stale fallback classification | yes | red-required | Test Contract Closure + JSON payload |
| cl-004 | S02 | negative | AC-004, EC-004 | zero Actions runs and status-only repos never become passed | no Actions runs plus legacy green status/check fixture | false green pass | yes | red-required | Test Contract Closure + wait decision evidence |
| cl-005 | S02 | edge | EC-001 | Actions API unavailable becomes unknown/human gate without fallback | permission/rate/schema/transient failure fixture | silent fallback to forbidden source | yes | red-required | limitations payload + test result |
| cl-006 | S02 | edge | EC-002 | failed run-level conclusion remains failed when jobs API is unavailable | run failed, jobs endpoint unavailable | masking failed CI as unknown/pass | yes | red-required | JSON payload + test result |
| cl-007 | S03 | compatibility | AC-002, AC-003, AC-004 | snapshot/wait progress and fingerprint use Actions summary, not legacy check fields | observation payload with deprecated legacy fields empty | downstream decision drift | yes | red-required | wait result + fingerprint test |
| cl-008 | S04 | regression | AC-005 | issue comments, PR reviews, review comments, reviewThreads remain present | PR fixture with review blockers and forbidden CI endpoints blocked | accidental review-observation weakening | yes | red-required | review payload test |
| cl-009 | S05 | acceptance | AC-006 | doctor does not require Checks/statuses/status rollup permissions for PR observation repair | token capability fixture without Checks/statuses permissions | false repair blocker | yes | red-required | doctor output test |
| cl-010 | S90 | docs | AC-007, EC-003, EC-005 | guidance says API/surface is forbidden, not the word `checks`; external checks are intentionally unobserved | shipped skills/templates/docs inspection | future rollback through confusing wording | yes | inspect-only | docs diff + spec-reviewer pass |
| cl-011 | S90 | docs | EC-005 | compatibility names may remain but must say Actions-only behavior | `fetch_pr_checks_snapshot.sh` and skill docs wording | accidental breaking rename or misleading compatibility | yes | inspect-only | docs diff + static scan |
| cl-012 | S99 | gate | workflow_issue.md | final QA/code/spec gates pass and report ledgers close all required rows | issue-wide diff and report evidence | incomplete delivery reported as complete | yes | manual-required | Final QA/Code/Spec Gate entries |

## 6. Test Strategy Mapping

- Forbidden-call tests:
  - Scope: S01.
  - Mechanism: fake `gh` fails on forbidden API/CLI/JSON surfaces; static scan targets endpoint and field names, not the word `checks` alone.
  - Report destination: `report.md` Test Contract Closure for cl-001.

- Actions state tests:
  - Scope: S02.
  - Mechanism: fixtures for success, failure, pending/queued/in_progress, cancelled/timed_out, zero runs, Actions unavailable, failed run with jobs unavailable.
  - Report destination: Test Contract Closure and Closure Coverage for cl-002 through cl-006.

- Snapshot/wait tests:
  - Scope: S03.
  - Mechanism: wait result, progress text, fingerprint stability, no decision use of legacy compatibility fields.
  - Report destination: Step Contract Closure for S03 and Closure Coverage cl-007.

- Review preservation tests:
  - Scope: S04.
  - Mechanism: PR review/comment/thread fixture with forbidden CI endpoint guard active.
  - Report destination: Test Contract Closure cl-008.

- Doctor tests:
  - Scope: S05.
  - Mechanism: `tests/cli_runtime/test_runtime_doctor_s04.py` fixtures where Actions and PR/comment reads are relevant, Checks/statuses/rollup are not repair targets.
  - Report destination: Test Contract Closure cl-009.

- Docs/static inspection:
  - Scope: S90.
  - Mechanism: inspect shipped skills/templates/docs for Actions-only wording, intentional loss wording, compatibility naming boundary, and absence of misleading status rollup fallback guidance.
  - Report destination: Step Contract Closure cl-010/cl-011 and Final Spec Review Gate.

## 7. Review Gates

- Per implementation step:
  - Worker: `dev-coder` for S01-S05.
  - Reviewer: `code-reviewer`.
  - Required state before commit: step-local verification passes, report evidence updated by main orchestrator, reviewer `review_status: pass`.
  - Commit rule: one implementation step equals one commit scope; final commit must not catch up uncommitted implementation work.

- Docs/skill wording step:
  - Worker: `doc-writer` for S90.
  - Reviewer: `spec-reviewer`.
  - Required state before commit: docs diff aligns with requirement/design/plan, no word-ban interpretation introduced, reviewer pass.

- Final quality gate:
  - `qa-reviewer`: issue-wide test sufficiency and integration test need.
  - issue-wide `code-reviewer`: integrated diff, responsibility boundaries, maintainability, regression risk.
  - final `spec-reviewer`: requirement/design/plan/report/implementation/tests/docs alignment.
  - Any fail requires bounded follow-up through the appropriate worker and fresh re-review.

## 8. Rollback / Compatibility

- Rollback boundary:
  - Reintroducing Checks API, commit statuses, status rollup, or `gh pr checks` equivalent requires a new ADR or explicit requirement change.
  - A local implementation rollback may revert a broken Actions-only implementation, but must not restore forbidden fallback as a silent repair.

- Compatibility:
  - Public shell entrypoints with `checks` in the name may remain as historical compatibility surfaces.
  - Legacy JSON fields may remain only as empty/deprecated metadata if downstream shape compatibility requires it.
  - Legacy fields must not participate in CI decision, wait progress, fingerprint, pass/fail classification, or limitation reasoning.
  - `ci.source_policy = "github_actions_only"` or equivalent marker should be present so downstream consumers and docs can distinguish compatibility shape from evidence source.

- Known intentional loss:
  - External/non-Actions required checks are not observed.
  - Status-only repositories do not become passed.
  - GitHub UI mergeability is not fully reproduced.

## 9. Docs Impact

S90 is required. Docs impact is not `none` because requirement/design explicitly require shipped skill/docs guidance updates and merge-preparer wording changes.

Docs targets from design:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh` usage text if needed
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` usage text if needed
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh` compatibility usage text
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`

S90 must state:

- Actions workflow runs/jobs are the only CI source of truth.
- Checks API/status rollup/commit statuses are intentionally not used.
- Missing Checks/statuses permissions are not a PR observation repair target.
- External/non-Actions checks are intentionally unobserved residual risk.
- `checks` named compatibility surfaces may remain, but they do not imply GitHub Checks API usage.

## 10. Final Quality Gate

S99 must run after every implementation/docs step is committed or approved-no-op with evidence.

Required final verification candidates:

- `uv run pytest tests/unit/infra/test_init_update.py`
- `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`
- A focused static scan or test assertion that forbidden endpoint/field/CLI surfaces are absent from live provider-side CI decision code, excluding historical docs/discussions and compatibility wording where explicitly allowed.
- Any focused observation script tests added during S01-S04.
- `./spec-dock/scripts/spec-dock validate` if the main orchestrator determines local dogfooding state is ready for validation.

Required final evidence:

- Final QA Gate: `qa-reviewer` verdict on AC/EC and missing high-value tests.
- Final Code Review Gate: issue-wide `code-reviewer` verdict on integrated diff.
- Final Spec Review Gate: `spec-reviewer` verdict that requirement/design/plan/report/docs align.
- Final Commit evidence: commit scope and post-commit clean check recorded outside the committed report or in delivery evidence as workflow requires.

## 11. Plan Blockers

- None identified from the supplied requirement/design/ADR/interview evidence.
- Potential execution blockers to watch:
  - Existing downstream consumers may rely on legacy `ci.check_runs` fields.
  - Fake-gh/static scans can become too broad if they ban the token `checks` instead of forbidden API surfaces.
  - Runtime command output may need path normalization when recording delegated artifacts, because the creation command returned a duplicated `spec-dock/spec-dock/...` prefix while the created file exists under `spec-dock/initiatives/...`.
  - If implementation needs to edit dogfooding mirror `.agents/` directly, stop and require plan amendment or explicit orchestrator decision; provider-side shipped assets remain source of truth.

## 12. Integration Notes for Main Orchestrator

- This draft should be treated as unreviewed discussion evidence until the main orchestrator adopts it into canonical `plan.md` and records disposition in `report.md` Evidence Adoption Ledger.
- Before adoption, run a fresh `spec-reviewer` pass against requirement/design/ADR/interview and this draft.
- If adopted, report should record:
  - discussion draft path
  - created_by_role: implementation-planner
  - scope_id: iss-00222
  - source_paths and intended_targets
  - adoption_status before/after orchestrator decision
  - diff guard result
  - whether canonical plan rows were copied, modified, or rejected
- Delegated evidence used:
  - none; this draft used only local source docs and no leaf sub-agent evidence.
- Forbidden actions avoided:
  - no canonical `requirement.md`, `design.md`, `plan.md`, or `report.md` edits
  - no implementation file edits
  - no tests/config/.agents/.github/GitHub state edits
  - no phase promotion, reviewer pass claim, implementation readiness claim, or final ownership claim

## Step Details

### S01 Forbidden CI Surface Guard And Collector Boundary

- Behavior goal:
  - CI collection uses no forbidden GitHub Checks API, commit status, PR status rollup, or `gh pr checks` equivalent surface.
- Design references:
  - `design.md` Interface Contract, Dependency Analysis, Test Strategy.
- Depends on:
  - requirement/design/ADR/interview source evidence.
- Unblocks:
  - S02, S03, S04.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
  - focused fake-gh fixtures/helpers already used by shipped skill tests.
- Planned contract:
  - Scope:
    - Remove or bypass forbidden collectors/fallbacks in CI collector.
    - Add fail-fast tests for forbidden calls.
    - Add source-policy marker or prepare the collector shape for S02 if the minimal S01 implementation needs it.
  - Test obligation:
    - closure id: cl-001, cl-011 where compatibility names are touched.
    - coverage rationale: AC-001 is the highest-risk regression and must fail if forbidden calls return.
  - Red / alternative evidence:
    - red-required: fake `gh` must fail if `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, or `gh pr checks` equivalent is requested.
    - covered-existing is insufficient unless the existing test demonstrably fails on every forbidden surface.
  - Green verification:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "observation or checks or github_pr"`
    - Static inspection of provider-side CI collector for forbidden decision calls.
  - Refactor guardrail:
    - Do not rename public compatibility scripts solely because they contain `checks`.
    - Do not change review/comment collector in this step.
  - Report evidence destination:
    - Implementation Delegation Gate S01
    - Step Contract Closure cl-001
    - Test Contract Closure cl-001
    - Closure Coverage cl-001
    - Reviewer Gate Status S01
    - Step Commit Gate S01
  - Amendment trigger:
    - Any need to retain forbidden API calls, change public script names broadly, or alter review/comment observation requires plan amendment and spec review.

#### S01 Delegation Contract

- Delegated role:
  - dev-coder.
- Input docs:
  - `requirement.md`
  - `design.md`
  - accepted ADR
  - compatibility interview
  - canonical `plan.md` after adoption
  - current target files.
- Allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
  - existing focused fake-gh helper/fixture paths if tests already use them.
- Forbidden changes:
  - canonical docs, report, GitHub state, `.agents/` dogfooding mirror as implementation source.
  - `pr_review_snapshot.py` behavior changes.
  - broad rename/removal of `checks` named compatibility surfaces.
- Acceptance criteria:
  - cl-001 passes; forbidden surfaces are never called in CI collection.
  - Compatibility names, if touched, remain clearly not GitHub Checks API usage.
- Required verification:
  - focused pytest command above plus static inspection.
- Reviewer focus:
  - code-reviewer verifies fake-gh sensitivity, no forbidden fallback, and narrow scope.
- Stop conditions:
  - Fake-gh framework cannot detect forbidden calls.
  - Required behavior appears to require a forbidden API.
  - Allowed paths are insufficient.
- Output required:
  - changed files
  - failing-first or characterization evidence
  - green command result
  - static inspection note
  - unresolved risks
  - `No material implementation decisions beyond the approved plan.` or a Ledger Note.

#### S01 Concrete Test Cases

- `tc-s01-001` negative: forbidden API calls fail the CI collector
  - Precondition: fake `gh` exits non-zero and logs when `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, or checks rollup equivalent is requested.
  - Action: run the PR observation CI collection path for a PR head SHA.
  - Expected result: no forbidden call is logged and the collector returns an Actions-only payload or non-pass Actions unavailable state.
  - Failure detection: any forbidden call fails the test even if final CI state would otherwise pass.
  - Verification method: focused test in `tests/unit/infra/test_init_update.py`.
  - Related closure id: cl-001.

- `tc-s01-002` static: compatibility names are not treated as a word ban
  - Precondition: provider-side source may still include historical names such as `fetch_pr_checks_snapshot.sh`.
  - Action: run or inspect the static forbidden-surface check.
  - Expected result: the scan targets forbidden endpoint/field/CLI usage, not every occurrence of `checks`.
  - Failure detection: a test that fails only because a compatibility filename contains `checks` is rejected as overbroad.
  - Verification method: code-reviewer inspection plus any static assertion added in the focused test.
  - Related closure id: cl-011.

#### S01 Step Closure Contract

- Close condition:
  - cl-001 is covered by red-required evidence and green verification.
  - No review/comment behavior changed.
- Residual risk:
  - Static scan exclusions must be reviewed carefully so historical docs do not hide live forbidden calls.

### S02 Actions-Only CI State Classification

- Behavior goal:
  - Actions workflow runs/jobs alone determine CI state, and zero/unavailable Actions evidence never becomes pass through legacy fallback.
- Design references:
  - `design.md` Adopted Policy, Interface Contract, Sequence Delta, Test Strategy.
- Depends on:
  - S01.
- Unblocks:
  - S03, S05, S90.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- Planned contract:
  - Scope:
    - Implement Actions run/job summary and classification.
    - Add explicit source policy marker such as `github_actions_only`.
    - Remove `ci_coverage_limited_to_github_actions` as a limitation.
  - Test obligation:
    - closure ids: cl-002, cl-003, cl-004, cl-005, cl-006.
  - Red / alternative evidence:
    - red-required fixtures for success, failure, pending/running, zero runs, Actions unavailable, and jobs unavailable with failed run.
  - Green verification:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "actions or observation or checks"`
  - Refactor guardrail:
    - Do not rewrite shell entrypoints except minimal payload/usage support needed by the collector.
  - Report evidence destination:
    - Implementation Delegation Gate S02
    - Step Contract Closure cl-002 through cl-006
    - Test Contract Closure cl-002 through cl-006
    - Closure Coverage cl-002 through cl-006
    - Reviewer Gate Status S02
    - Step Commit Gate S02
  - Amendment trigger:
    - New status vocabulary, changed pass/fail semantics beyond design, or any need for external CI source requires plan amendment.

#### S02 Delegation Contract

- Delegated role:
  - dev-coder.
- Input docs:
  - requirement/design/ADR/interview
  - adopted `plan.md`
  - S01 result evidence
  - current collector and tests.
- Allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
  - existing test fixtures/helpers required for the focused cases.
- Forbidden changes:
  - doctor/docs/merge-preparer wording; those are S05/S90.
  - review/comment collector behavior.
  - GitHub UI mergeability or branch protection inference.
- Acceptance criteria:
  - AC-002, AC-003, AC-004 and EC-001, EC-002, EC-004 close through Actions-only fixtures.
- Required verification:
  - focused pytest command and JSON payload inspection from test assertions.
- Reviewer focus:
  - code-reviewer checks status classification, no fallback, source-policy marker, and edge-case coverage.
- Stop conditions:
  - Existing payload shape cannot support downstream consumers without broader compatibility design.
  - Jobs API behavior cannot be modeled with current fixtures.
- Output required:
  - changed files
  - test result
  - payload shape notes
  - unresolved compatibility risks
  - Ledger Note if any field contract changes exceed design.

#### S02 Concrete Test Cases

- `tc-s02-001` acceptance: Actions success passes
  - Precondition: current head SHA has Actions workflow runs/jobs with terminal success.
  - Action: run CI collection.
  - Expected result: CI state is passed and no Checks/statuses limitation is emitted.
  - Failure detection: passed depends on forbidden legacy fields or missing source-policy marker.
  - Verification method: focused pytest fixture.
  - Related closure id: cl-002.

- `tc-s02-002` acceptance: Actions non-success states do not pass
  - Precondition: fixtures cover failure, queued, in_progress, pending, cancelled, timed_out, and unknown combinations.
  - Action: run CI collection for each fixture.
  - Expected result: each state maps to failed, pending, running, or unknown according to Actions evidence only.
  - Failure detection: any state becomes passed through check-runs/statuses fallback.
  - Verification method: parameterized focused pytest.
  - Related closure id: cl-003.

- `tc-s02-003` negative: zero Actions runs do not pass
  - Precondition: Actions runs list is empty and legacy check/status fixtures would be green if called.
  - Action: run CI collection.
  - Expected result: CI is none/unknown/human gate, never passed, and legacy fixtures are not called.
  - Failure detection: pass state or legacy call log entry.
  - Verification method: focused pytest with fake-gh forbidden guard.
  - Related closure id: cl-004.

- `tc-s02-004` edge: Actions unavailable does not fallback
  - Precondition: Actions API returns permission denied, rate limit, transient failure, or malformed response.
  - Action: run CI collection.
  - Expected result: output records unavailable/unknown/human gate and no forbidden fallback.
  - Failure detection: fallback to check-runs/statuses or missing limitation/diagnostic.
  - Verification method: focused pytest fixture.
  - Related closure id: cl-005.

- `tc-s02-005` edge: failed run remains failed when jobs are unavailable
  - Precondition: run-level conclusion is failure and jobs endpoint is unavailable.
  - Action: run CI collection.
  - Expected result: CI failed is preserved and job detail unavailable is recorded.
  - Failure detection: failed run becomes unknown/pass or check-runs fallback is called.
  - Verification method: focused pytest fixture.
  - Related closure id: cl-006.

#### S02 Step Closure Contract

- Close condition:
  - cl-002 through cl-006 have passing tests and reviewer pass.
- Residual risk:
  - Downstream consumers may need S03 changes before the whole issue is usable.

### S03 Snapshot/Wait Compatibility And Decision Consumption

- Behavior goal:
  - Snapshot and wait flows consume Actions-only CI payload without deriving decisions from legacy compatibility fields.
- Depends on:
  - S02.
- Unblocks:
  - S90, S99.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh` only if minimal compatibility usage text is inseparable from behavior
  - focused tests in existing shipped asset test files.
- Planned contract:
  - Scope:
    - Update progress/fingerprint/wait decision to use Actions summary and source policy.
    - Keep legacy fields empty/deprecated if needed, not evidence.
  - Test obligation:
    - closure id: cl-007 and downstream portions of cl-002 through cl-004.
  - Red / alternative evidence:
    - red-required wait/snapshot fixture where legacy fields are contradictory or empty.
  - Green verification:
    - focused pytest around wait/snapshot plus S02 collector tests.
  - Refactor guardrail:
    - Do not restructure all observation scripts; only change consumers of CI payload.
  - Report evidence destination:
    - Implementation Delegation Gate S03
    - Step Contract Closure cl-007
    - Test Contract Closure cl-007
    - Closure Coverage cl-007
    - Reviewer Gate Status S03
    - Step Commit Gate S03
  - Amendment trigger:
    - Removing public payload fields, changing shell entrypoint contract, or claiming GitHub UI mergeability needs plan amendment.

#### S03 Delegation Contract

- Delegated role:
  - dev-coder.
- Input docs:
  - requirement/design/ADR/interview
  - adopted `plan.md`
  - S02 payload evidence
  - target snapshot/wait files.
- Allowed paths:
  - `pr_observation_snapshot.py`
  - `pr_observation_wait.py`
  - existing focused tests/fixtures.
- Forbidden changes:
  - Doctor migration; S05 owns it.
  - Skill/docs wording; S90 owns it unless a script usage line is required for behavior compatibility.
  - Broad JSON contract removal without design amendment.
- Acceptance criteria:
  - Wait/snapshot behavior uses Actions-only payload and does not derive pass/fail from legacy compatibility fields.
- Required verification:
  - focused tests plus payload/fingerprint inspection.
- Reviewer focus:
  - code-reviewer checks downstream consistency, compatibility fields, and no hidden fallback.
- Stop conditions:
  - Downstream contract cannot be preserved without canonical design change.
- Output required:
  - changed files
  - verification result
  - payload/fingerprint compatibility note
  - unresolved downstream risk.

#### S03 Concrete Test Cases

- `tc-s03-001` compatibility: wait uses Actions summary
  - Precondition: snapshot payload has Actions success summary and empty/deprecated legacy fields.
  - Action: run wait decision path.
  - Expected result: wait can conclude eligible/passed from Actions summary only.
  - Failure detection: wait requires non-empty `ci.check_runs` or required check rollup.
  - Verification method: focused pytest.
  - Related closure id: cl-007.

- `tc-s03-002` negative: contradictory legacy fields do not override Actions
  - Precondition: test fixture injects deprecated legacy fields that would imply pass/fail differently from Actions.
  - Action: run snapshot/wait fingerprint and decision logic.
  - Expected result: decision and fingerprint use Actions summary and source policy, not legacy fields.
  - Failure detection: legacy field changes alter CI decision.
  - Verification method: focused pytest or characterization test.
  - Related closure id: cl-007.

#### S03 Step Closure Contract

- Close condition:
  - cl-007 passes and S02 behavior still passes.
- Residual risk:
  - External consumers outside tests may parse deprecated fields; S90 must document compatibility semantics.

### S04 Review/Comment/Thread Preservation Regression

- Behavior goal:
  - Review/comment/thread observation remains intact while CI forbidden surfaces are blocked.
- Depends on:
  - S01.
- Unblocks:
  - S99.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` inspection only unless regression requires a narrow fix.
  - `pr_observation_snapshot.py` only if integration payload assembly needs a narrow adjustment.
  - focused tests in existing shipped asset test files.
- Planned contract:
  - Scope:
    - Verify issue comments, PR reviews, review comments, requested reviewers/teams, GraphQL reviewThreads, and reviewDecision remain present.
    - Keep review GraphQL separate from CI rollup GraphQL.
  - Test obligation:
    - closure id: cl-008.
  - Red / alternative evidence:
    - red-required regression fixture if existing tests do not cover review payload with forbidden CI guard active.
  - Green verification:
    - focused pytest around review payload.
  - Refactor guardrail:
    - Do not remove review GraphQL because `statusCheckRollup` is forbidden; only CI rollup fields are forbidden.
  - Report evidence destination:
    - Implementation Delegation Gate S04
    - Step Contract Closure cl-008
    - Test Contract Closure cl-008
    - Closure Coverage cl-008
    - Reviewer Gate Status S04
    - Step Commit Gate S04
  - Amendment trigger:
    - Any weakening of review/comment evidence or removal of reviewThreads requires plan amendment and likely requirement/design revisit.

#### S04 Delegation Contract

- Delegated role:
  - dev-coder.
- Input docs:
  - requirement AC-005
  - design review/comment payload contract
  - adopted `plan.md`
  - S01 forbidden guard evidence.
- Allowed paths:
  - focused review/snapshot tests
  - `pr_review_snapshot.py` only for narrow preservation fixes
  - `pr_observation_snapshot.py` only for payload integration fixes.
- Forbidden changes:
  - CI collector classification changes; S02 owns them.
  - Removing reviewThreads or reviewDecision observation.
  - Treating all GraphQL as forbidden.
- Acceptance criteria:
  - AC-005 closes while forbidden CI calls remain blocked.
- Required verification:
  - focused pytest with review/comment/thread fixture.
- Reviewer focus:
  - code-reviewer checks boundary between review GraphQL and forbidden CI rollup.
- Stop conditions:
  - Review fixture cannot distinguish CI rollup GraphQL from review thread GraphQL.
- Output required:
  - changed files or approved-no-op evidence
  - verification result
  - review payload note
  - unresolved risk.

#### S04 Concrete Test Cases

- `tc-s04-001` regression: review evidence survives Actions-only change
  - Precondition: PR fixture includes issue comments, PR reviews, review comments, unresolved reviewThreads, and forbidden CI endpoints blocked.
  - Action: run observation snapshot/review collection.
  - Expected result: review payload includes the review/comment/thread evidence and CI guard logs no forbidden calls.
  - Failure detection: review blockers disappear or forbidden CI endpoint is called.
  - Verification method: focused pytest.
  - Related closure id: cl-008.

- `tc-s04-002` boundary: review GraphQL is not status rollup
  - Precondition: GraphQL reviewThreads query is allowed, but `statusCheckRollup` field is forbidden.
  - Action: inspect or test GraphQL query construction.
  - Expected result: reviewThreads/reviewDecision are retained and no status rollup field is requested.
  - Failure detection: removing reviewThreads or requesting `statusCheckRollup`.
  - Verification method: focused pytest or code-reviewer inspection.
  - Related closure id: cl-008.

#### S04 Step Closure Contract

- Close condition:
  - cl-008 passes or is approved-no-op with existing coverage and reviewer agreement.
- Residual risk:
  - GitHub API schema drift for reviewThreads remains outside this issue unless detected by tests.

### S05 Doctor/Capability Migration

- Behavior goal:
  - Doctor/capability diagnostics stop treating Checks/statuses/status rollup permissions as PR observation repair requirements.
- Depends on:
  - S02.
- Unblocks:
  - S90, S99.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
- Planned contract:
  - Scope:
    - Change PR observation capability model to Actions read plus PR/comment read.
    - Remove repair guidance for Checks/statuses/status rollup permissions from PR observation path.
  - Test obligation:
    - closure id: cl-009.
  - Red / alternative evidence:
    - red-required doctor fixture without Checks/statuses permissions.
  - Green verification:
    - `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`
  - Refactor guardrail:
    - Do not change unrelated doctor capabilities or GitHub mutation permissions.
  - Report evidence destination:
    - Implementation Delegation Gate S05
    - Step Contract Closure cl-009
    - Test Contract Closure cl-009
    - Closure Coverage cl-009
    - Reviewer Gate Status S05
    - Step Commit Gate S05
  - Amendment trigger:
    - Need to change global doctor capability schema beyond PR observation requires plan amendment.

#### S05 Delegation Contract

- Delegated role:
  - dev-coder.
- Input docs:
  - requirement AC-006
  - design doctor capability section
  - adopted `plan.md`
  - current doctor/capability tests.
- Allowed paths:
  - `github_capability_cli.py`
  - `doctor.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
  - narrow fixtures used by that test.
- Forbidden changes:
  - Observation script implementation.
  - Docs/skill wording outside runtime doctor output; S90 owns shipped docs wording.
  - GitHub write capability changes.
- Acceptance criteria:
  - AC-006 closes and doctor output no longer asks users to repair missing Checks/statuses/status rollup permission for PR observation.
- Required verification:
  - `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`.
- Reviewer focus:
  - code-reviewer checks capability boundaries and unrelated doctor behavior.
- Stop conditions:
  - Doctor architecture cannot represent Actions/read and review/comment/read separately without broader design.
- Output required:
  - changed files
  - test result
  - diagnostic wording note
  - unresolved capability risk.

#### S05 Concrete Test Cases

- `tc-s05-001` acceptance: doctor does not require Checks/statuses permissions
  - Precondition: capability fixture has Actions read and PR/comment read, but lacks Checks and Commit statuses permissions.
  - Action: run doctor S04 capability diagnostic.
  - Expected result: PR observation capability is not blocked by missing Checks/statuses/status rollup permission.
  - Failure detection: output recommends repairing Checks/statuses/status rollup for PR observation.
  - Verification method: `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`.
  - Related closure id: cl-009.

- `tc-s05-002` negative: missing Actions read remains diagnostic
  - Precondition: capability fixture lacks Actions read.
  - Action: run doctor S04 capability diagnostic.
  - Expected result: Actions read is still reported as relevant for PR observation.
  - Failure detection: doctor under-reports actual Actions observation blocker.
  - Verification method: focused doctor test.
  - Related closure id: cl-009.

#### S05 Step Closure Contract

- Close condition:
  - cl-009 passes and unrelated doctor behavior remains stable.
- Residual risk:
  - Review/comment read permission wording may need S90 docs alignment.

### S90 Docs Impact Resolution And Skill Wording

- Behavior goal:
  - Shipped guidance reflects Actions-only CI observation, intentional losses, compatibility names, and doctor capability boundaries.
- Depends on:
  - S02, S03, S05.
- Unblocks:
  - S99.
- Target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh` if usage text requires it
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` if usage text requires it
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- Planned contract:
  - Scope:
    - Document Actions-only CI source.
    - Document external/non-Actions checks as intentionally unobserved.
    - Document compatibility names without implying GitHub Checks API usage.
    - Update merge-preparer wording so it does not overclaim all GitHub required checks are observed.
  - Test obligation:
    - closure ids: cl-010, cl-011.
  - Red / alternative evidence:
    - inspect-only is acceptable because this is docs/skill wording.
  - Green verification:
    - docs diff inspection
    - focused static scan for misleading forbidden fallback wording where practical
    - spec-reviewer docs/spec alignment pass.
  - Refactor guardrail:
    - Do not change runtime behavior in S90.
    - Do not rewrite historical discussions or report evidence.
  - Report evidence destination:
    - Implementation Delegation Gate S90
    - Step Contract Closure cl-010/cl-011
    - Test Contract Closure cl-010/cl-011 as inspect-only
    - Closure Coverage cl-010/cl-011
    - Reviewer Gate Status S90
    - Step Commit Gate S90
    - Final Spec Review Gate input.
  - Amendment trigger:
    - Need to rename public compatibility surfaces, change user-facing workflow semantics, or claim complete GitHub UI mergeability requires plan/design amendment.

#### S90 Delegation Contract

- Delegated role:
  - doc-writer.
- Input docs:
  - requirement/design/ADR/interview
  - adopted `plan.md`
  - S02/S03/S05 implementation evidence
  - target shipped skill/docs/template files.
- Allowed paths:
  - docs/skill/template paths listed in S90 target files.
- Forbidden changes:
  - Runtime Python or test files.
  - canonical requirement/design/plan/report.
  - historical discussions.
  - `.agents/` dogfooding mirror as source of truth.
- Acceptance criteria:
  - AC-007, EC-003, EC-005 close in shipped guidance.
- Required verification:
  - docs diff inspection and spec-reviewer docs/spec alignment.
- Reviewer focus:
  - spec-reviewer checks no API/word-ban confusion, no mergeability overclaim, and consistency with requirement/design.
- Stop conditions:
  - Wording cannot be aligned without changing canonical requirement/design.
- Output required:
  - changed docs files
  - inspection result
  - residual docs risk
  - `No material implementation decisions beyond the approved plan.` or Ledger Note.

#### S90 Concrete Test Cases

- `tc-s90-001` inspect-only: Actions-only guidance is explicit
  - Precondition: shipped skill docs are updated by doc-writer.
  - Action: inspect `github-pr-observation/SKILL.md` and relevant script usage text.
  - Expected result: guidance says Actions workflow runs/jobs are the only CI source of truth.
  - Failure detection: guidance still describes supplemental Checks/statuses/status rollup fallback.
  - Verification method: docs diff inspection and spec-reviewer pass.
  - Related closure id: cl-010.

- `tc-s90-002` inspect-only: compatibility names are not a word ban
  - Precondition: compatibility files or fields with `checks` in the name remain.
  - Action: inspect docs and compatibility usage wording.
  - Expected result: wording explains historical naming and forbids GitHub Checks API usage, not the token `checks`.
  - Failure detection: docs require deleting every `checks` token or imply compatibility names call Checks API.
  - Verification method: docs diff inspection.
  - Related closure id: cl-011.

- `tc-s90-003` inspect-only: merge-preparer does not overclaim UI checks
  - Precondition: merge-preparer skill/template wording is updated.
  - Action: inspect merge-preparer guidance.
  - Expected result: merge readiness wording is limited to observed Actions CI and review/thread evidence, with external/non-Actions checks recorded as intentionally unobserved residual risk when relevant.
  - Failure detection: wording claims complete GitHub UI required-check coverage.
  - Verification method: docs diff inspection and spec-reviewer pass.
  - Related closure id: cl-010.

#### S90 Step Closure Contract

- Close condition:
  - cl-010 and cl-011 inspect-only closure passes with spec-reviewer approval.
- Residual risk:
  - Consumer workflows may still carry old mental model from compatibility filenames; wording must be direct.

### S99 Final Quality Gate

- Behavior goal:
  - Confirm issue-wide implementation, tests, docs, report evidence, and reviewer gates close all required requirements.
- Depends on:
  - S01-S05 and S90.
- Target files:
  - Canonical `report.md` evidence integration by main orchestrator.
  - No new runtime/docs mutation unless a final reviewer finding triggers bounded follow-up.
- Planned contract:
  - Scope:
    - Run final validation and reviews.
    - Confirm closure index coverage.
    - Confirm no forbidden paths were edited outside approved steps.
  - Test obligation:
    - closure id: cl-012.
  - Red / alternative evidence:
    - manual-required final gate evidence.
  - Green verification:
    - focused test commands from S01-S05
    - any added observation script tests
    - `./spec-dock/scripts/spec-dock validate` when local dogfooding state is suitable
    - `git status --short` and `git diff --name-only` inspection.
  - Refactor guardrail:
    - Final gate must not become catch-up implementation.
  - Report evidence destination:
    - Final QA Gate
    - Final Code Review Gate
    - Final Spec Review Gate
    - Closure Coverage
    - Closure Delta
    - Final Commit
    - PR Delivery Gate and Merge Preparation Gate later in delivery flow if main orchestrator continues beyond planning.
  - Amendment trigger:
    - Missing required test, failed final reviewer gate, open decision ledger entry, or closure index mismatch requires bounded follow-up and re-review.

#### S99 Delegation Contract

- Delegated roles:
  - qa-reviewer for test sufficiency.
  - code-reviewer for issue-wide integrated diff.
  - spec-reviewer for final spec alignment.
- Input docs:
  - requirement/design/plan/report
  - all S01-S90 changed files and evidence
  - closure index and test results.
- Allowed paths:
  - `report.md` evidence updates by main orchestrator.
  - No implementation/docs paths unless a reviewer finding produces a bounded follow-up step.
- Forbidden changes:
  - Catch-up implementation in final commit.
  - Marking reviewer unavailable/waived/provisional as pass.
  - Phase promotion or issue finish without required evidence.
- Acceptance criteria:
  - cl-012 closes; all required closure rows have evidence.
- Required verification:
  - final test suite subset and reviewer passes.
- Reviewer focus:
  - QA: obligation coverage and missing tests.
  - Code: integrated diff and responsibility boundaries.
  - Spec: requirement/design/plan/report/docs alignment.
- Stop conditions:
  - Any final gate fails.
  - Report has unresolved delegated evidence adoption entry or open decision ledger.
  - Worktree contains unreviewed implementation changes from previous steps.
- Output required:
  - final verification commands and results
  - reviewer verdicts
  - closure coverage summary
  - unresolved risk or `none`
  - final commit/delivery evidence destination.

#### S99 Concrete Test Cases

- `tc-s99-001` manual-required: final closure coverage is complete
  - Precondition: S01-S05 and S90 are closed as committed or approved-no-op.
  - Action: inspect report closure ledgers against the Spec-Locked Closure Index.
  - Expected result: every required closure id cl-001 through cl-012 has evidence and disposition.
  - Failure detection: missing evidence, open closure delta, or unresolved delegated artifact adoption.
  - Verification method: manual inspection plus final spec-reviewer pass.
  - Related closure id: cl-012.

- `tc-s99-002` manual-required: final reviews pass
  - Precondition: issue-wide diff and test evidence are ready.
  - Action: run qa-reviewer, issue-wide code-reviewer, and final spec-reviewer.
  - Expected result: all three return pass; any fail is resolved through bounded follow-up and re-review.
  - Failure detection: unavailable, waived, provisional, or failed review treated as pass.
  - Verification method: reviewer evidence in report.
  - Related closure id: cl-012.

#### S99 Step Closure Contract

- Close condition:
  - Final QA, code, and spec gates pass.
  - Report ledgers close all required rows.
  - No uncommitted implementation/docs changes remain outside intended final evidence handling.
- Residual risk:
  - PR delivery and merge preparation remain separate workflow gates after local implementation closure.

## Final Exit Contract

- The canonical plan, if adopted, should require:
  - all AC/EC and constraints mapped to closure ids
  - S01-S05 and S90 closed as committed or approved-no-op
  - S99 final QA/code/spec pass
  - report evidence for delegation, closure, tests, reviewer gates, commit gates, docs impact, final gates, and any adoption decision
  - no unresolved plan blockers or open decision ledger entries
  - no claim that external/non-Actions checks or full GitHub UI mergeability are observed

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
