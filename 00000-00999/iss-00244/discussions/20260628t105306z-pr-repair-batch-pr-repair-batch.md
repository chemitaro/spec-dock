---
種別: pr-repair-batch
ID: "20260628t105306z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "active"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260628t105306z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/245
- PR number: 245
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation
- Latest head SHA: bed5f273fa2b9de8743d226d156fb1be65fd2775
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 245 --head-sha bed5f273fa2b9de8743d226d156fb1be65fd2775 --trigger-mode post-once ...`
- Observation final JSON / evidence: `/private/tmp/spec-dock-iss-00244-pr245-observation-bed5f273/result.json`
- Observation status: `human_gate`; CI passed; review has 5 unresolved current threads.
- Trigger comment id: 4825825846
- Trigger created_at: 2026-06-28T10:37:52Z
- Trigger boundary: explicit post-once trigger for head `bed5f273fa2b9de8743d226d156fb1be65fd2775`
- Resume metadata: N/A for repair; re-observe latest head after repair push.
- New trigger approved: no
- Observation limitation: none
- Batch status: implemented; 6 inventory items triaged into 4 repair units; local validation passed; re-observation pending after push.

## Batch Purpose

Use this batch to triage review findings, observed GitHub Actions CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision. PR observation intentionally does not observe external/non-Actions checks; record GitHub UI or external CI confirmation as residual risk or a human gate when branch protection depends on them.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Plan readiness accepts scaffold / draft plan as executable | I001 | `_classify_plan_text` accepts template markers before checking draft/scaffold status. | U001 | Protected execution-ready handoff. |
| C002 | PR observation decision semantics regressions | I002, I003, I004 | Observation wait/review snapshot logic added forbidden rollup input and incomplete blocker-policy completion/protected-domain handling. | U002 | Protected PR observation / merge-prepared semantics. |
| C003 | Assurance contract unknown root fields are accepted then dropped on rewrite | I005 | Payload parser accepts additive root fields but dataclass canonicalization rewrites only known fields. | U003 | Public assurance contract surface. |
| C004 | Provider CI rollup tests still expected timeout after rollup removal | I006 | Three tests retained old wait/timeout expectations even though Actions passed + review approved should now become merge-prepared. | U004 | CI-only blocker found by re-observation. |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | review_feedback | C001 | review_feedback:plan-readiness | thread `PRRT_kwDOQ99OK86Myv-a`, comment `3487750613`, `workflow.py:196` | Standard issue generated scaffold/draft plan can be classified executable. | valid | blocking | yes | fix-now | U001 | implemented | Execution-ready handoff must not become ready on placeholder plan. | Re-observation pending. |
| I002 | review_feedback | C002 | review_feedback:pr-observation-rollup | thread `PRRT_kwDOQ99OK86Myv-b`, comment `3487750614`, `pr_observation_wait.py:127` | Wait logic reads `mergeStateStatus,statusCheckRollup` despite Actions-only contract. | valid | blocking | yes | fix-now | U002 | implemented | Skill forbids PR status rollup/check-rollup as CI evidence. | Re-observation pending. |
| I003 | review_feedback | C002 | review_feedback:blocker-policy-completion | thread `PRRT_kwDOQ99OK86Myv-c`, comment `3487750615`, `pr_review_snapshot.py:1205` | `blocker_policy_no_action` can pass decision but still be treated as no-completion evidence. | valid | blocking | yes | fix-now | U002 | implemented | Non-blocking-only review must not become review-completion-unknown. | Re-observation pending. |
| I004 | review_feedback | C002 | review_feedback:protected-domain-promotion | thread `PRRT_kwDOQ99OK86Myv-d`, comment `3487750616`, `pr_review_snapshot.py:1003` | Protected domain whitelist omits workflow/CI/review/schema/dependency domains from the review policy. | valid | blocking | yes | fix-now | U002 | implemented | Machine-evidenced P2 in protected PR domains must promote. | Re-observation pending. |
| I005 | review_feedback | C003 | review_feedback:assurance-contract-schema | thread `PRRT_kwDOQ99OK86Myv-f`, comment `3487750618`, `assurance_store.py:220` | Unknown root fields are accepted by read but dropped by compose rewrite. | valid | blocking | yes | fix-now | U003 | implemented | Public contract behavior must be consistent. | Re-observation pending. |
| I006 | check_failure | C004 | check_failure:Provider CI/provider-tests | run `28320468406`, job `83901426510` | Provider CI failed because rollup-related tests still expected `timeout` after rollup state was removed from the decision path. | valid | blocking | yes | fix-now | U004 | implemented | CI must pass before merge-prepared; tests should assert the new Actions-only contract. | Re-observation pending. |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<actions_job_or_workflow_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### CXXX

### C001

- Covered inventory IDs: I001
- Validity analysis: Valid. Current plan readiness detection can match generic template phrases before excluding draft/scaffold plan artifacts.
- Need-to-fix decision: fix-now
- Root cause: Marker-based executable detection is too permissive.
- Options considered: require `状態: approved`; reject draft/template; require concrete step section. Recommended to reject draft/template and managed placeholder text, while preserving existing executable tests.
- Recommended disposition: U001
- Rationale: This is protected execution-ready handoff behavior.
- Residual risk: none after focused tests and PR re-observation.

### C002

- Covered inventory IDs: I002, I003, I004
- Validity analysis: Valid. All three affect protected PR observation / merge-prepared semantics.
- Need-to-fix decision: fix-now
- Root cause: Review/observation policy implementation drifted from the Actions-only and blocker-centric contract.
- Options considered: keep rollup as external residual risk; remove rollup completely. Recommended to remove rollup from decision path and tighten blocker policy completion/protected domain logic.
- Recommended disposition: U002
- Rationale: These determine whether PRs are merge-prepared or human-gated.
- Residual risk: external/non-Actions checks remain intentionally unobserved by this skill and must not be claimed as observed.

### C003

- Covered inventory IDs: I005
- Validity analysis: Valid. Read accepts unknown root keys but rewrite drops them.
- Need-to-fix decision: fix-now
- Root cause: Schema validation does not reject unknown root keys before dataclass canonicalization.
- Options considered: preserve unknown root fields or reject them. Recommended to reject unknown root fields for a strict public contract.
- Recommended disposition: U003
- Rationale: Rejecting unknown fields avoids silent data loss and keeps canonical serialization simple.
- Residual risk: additive root metadata must be introduced through an explicit schema change.

### C004

- Covered inventory IDs: I006
- Validity analysis: Valid. The failed tests encoded old rollup-blocking semantics and were timing-sensitive.
- Need-to-fix decision: fix-now
- Root cause: Test expectations were not fully realigned after U002 removed `mergeStateStatus,statusCheckRollup` from the wait decision path.
- Options considered: retain timeout expectation, remove tests, or update tests to assert merge-prepared. Recommended to update tests and keep rollup fields in the scenario so the regression remains covered.
- Recommended disposition: U004
- Rationale: This is the only observed Provider CI blocker after the initial repair push.
- Residual risk: none after local full `test_init_update.py`, lint, and PR re-observation.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260628t105306z-pr-repair-batch | I001 | fix-now | blocking | `20260628t105407z-disc-pr-repair-unit-u001-plan-readiness.md` | implemented | Tighten plan readiness classifier and add regression test. | pending after push | none expected |
| U002 | 20260628t105306z-pr-repair-batch | I002, I003, I004 | fix-now | blocking | `20260628t105406z-disc-pr-repair-unit-u002-pr-observation-decision.md` | implemented | Remove rollup decision path; treat blocker-policy no-action as explicit completion; expand protected-domain vocabulary; add focused regressions. | pending after push | external/non-Actions checks intentionally unobserved |
| U003 | 20260628t105306z-pr-repair-batch | I005 | fix-now | blocking | `20260628t105408z-disc-pr-repair-unit-u003-assurance-contract-unknown-fields.md` | implemented | Reject unknown `.assurance.json` root fields and test invalid-schema behavior. | pending after push | schema extensions require explicit fields |
| U004 | 20260628t105306z-pr-repair-batch | I006 | fix-now | blocking | `20260628t114108z-disc-pr-repair-unit-u004-provider-ci-rollup-tests.md` | implemented | Update rollup-related wait tests to assert `passed` / `merge_prepared` under the new Actions-only contract. | pending after push | none expected |

## Implementation / Validation Result

- U001 implemented in provider and dogfooding `workflow.py`; draft/scaffold/template plan markers are rejected before executable markers.
- U002 implemented in provider and installed `github-pr-observation` scripts; PR status rollup is removed from the decision path, `blocker_policy_no_action` is treated as explicit completion, and protected-domain promotion vocabulary now covers the repository's workflow/review/schema/dependency surfaces.
- U003 implemented in provider and dogfooding `assurance_store.py`; unknown `.assurance.json` root fields now produce `invalid_schema` instead of being silently dropped by canonical serialization.
- Validation passed:
  - `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/infra/test_init_update.py -k 'issue_244_wait_script_does_not_define_required_check_rollup_reader or issue_232_protected_domain or blocker_policy_no_action or status_rollup_failure_is_ignored or status_rollup_running_is_ignored or draft_placeholder_plan or unknown_root_field'` -> 15 passed.
  - `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/application/test_assurance.py tests/cli_runtime/test_assurance.py` -> 43 passed.
  - `uv run pytest tests/unit/infra/test_init_update.py` -> 521 passed.
  - `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_keeps_required_checks_pending_as_wait tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_244_pr_observation_wait_ignores_failed_required_rollup tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_244_pr_observation_wait_ignores_failed_required_status_state` -> 3 passed after U004.
  - `uv run pytest tests/unit/infra/test_init_update.py` -> 521 passed after U004.
  - `make lint` -> ruff check, ruff format check, and mypy passed.
  - `git diff --check` -> passed.
- Commit evidence and re-observation result are pending until commit, push, and PR observation for the new head SHA complete.

## Unit Discussion Plan

Create a repair unit `disc` for each `fix-now` item and each `needs-human` item that needs implementation analysis, design judgment, or options comparison. The worker must use the repair unit discussion, not raw findings, as the source of truth.

Required repair unit checklist:

- `source_batch`
- `unit_id`
- `covered_ids`
- `source_links`
- `failure_class`
- `risk_class`
- `disposition`
- `Validity Analysis`
- `Need-To-Fix Decision`
- `Root Cause`
- `Options Considered`
- `Recommended Design`
- `Implementation Plan`
- `Validation Plan`
- `Implementation Result`
- `Commit Evidence`
- `Re-observation Result`
- `Residual Risk / Follow-up`

## Stop Conditions

Stop at a human gate when any condition applies:

- Any inventory item remains `untriaged`.
- Any unresolved `needs-human` item remains.
- A `blocking` `fix-now` repair unit is incomplete or repeatedly fails.
- Observation output is not for the latest head SHA.
- Timeout or observation limitation lacks resume metadata.
- Resume would cross the recorded trigger boundary.
- A new trigger would be required but has not been approved.
- Scope expansion, requirement expansion, breaking change, migration, secret, deployment setting, permission/auth, external/flaky, or ambiguous review intent is involved.
- Loop limits for the same failure class or total repair attempts are reached.

## Merge-Prepared Gate

Report `merge-prepared: yes` only when all conditions are true:

- PR is open.
- Latest head re-observation is complete and matches the latest head SHA.
- No observed GitHub Actions CI failure remains.
- External/non-Actions check state has either been confirmed outside PR observation or is recorded as a human gate/residual risk; do not treat missing Checks API/status rollup evidence as observed pass evidence.
- No blocking review feedback remains.
- No visible merge conflict or equivalent merge blocker remains.
- No `untriaged` inventory item remains.
- No unresolved `needs-human` item remains.
- No `blocking` item has an incomplete `fix-now` repair unit.
- Every `follow-up`, `no-action`, `covered-by`, `duplicate`, or `false-positive` item has rationale and residual risk where relevant.
- Observation limitation handling, resume metadata, trigger boundary, and new trigger approval status are recorded.
- Review-thread unresolved state is known, or any unresolved-thread limitation is explicitly waived and recorded as residual risk.
- `review-clean` is reported separately from `merge-prepared`; `review-clean: no` may still be `merge-prepared: yes` when all remaining items are triaged and non-blocking.
