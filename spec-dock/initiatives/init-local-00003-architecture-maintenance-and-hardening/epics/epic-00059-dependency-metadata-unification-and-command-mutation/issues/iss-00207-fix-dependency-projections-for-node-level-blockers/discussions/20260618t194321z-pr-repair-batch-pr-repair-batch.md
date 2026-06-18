---
種別: pr-repair-batch
ID: "20260618t194321z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00207"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260618t194321z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/208
- PR number: 208
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00207-fix-dependency-projections-for-node-level-blockers
- Latest head SHA: b506e0abcc8749bc679d28c78f71efcfa170fb9b
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 208 --head-sha 8ca6cd6e1c7a9899b20b69445c61343e2b455633`
- Observation final JSON / evidence: stdout JSON from observation at 2026-06-18T19:43:11Z
- Observation status: human_gate; CI passed; review unresolved after U001 re-observation
- Trigger comment id: 4745456367
- Trigger created_at: 2026-06-18T19:29:48Z
- Trigger boundary: current trigger boundary for head SHA 8ca6cd6e1c7a9899b20b69445c61343e2b455633
- Resume metadata: N/A; initial observation reached terminal human_gate
- New trigger approved: no
- Observation limitation: none; unresolved review thread state known
- Batch status: U002 implemented; re-observation pending

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | high-level readiness evaluation must respect completed source issues and cached high-level state | I001, I002 | node blocker evaluation applies to done source issues; cached status context reads issue-only `status` instead of high-level `github.state` | U001 | Both findings affect high-level dependency readiness context |
| C002 | offline cached high-level state must use generated artifact schema across check/sync/active paths | I003, I004, I005 | cached high-level state reader checks `kind` instead of generated `type`; sync and active-set paths do not receive cached high-level state | U002 | Same cached state propagation problem across offline workflows |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | codex_review_comment | C001 | review_feedback:completed-source-node-blocker | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py:190`, thread `PRRT_kwDOQ99OK86KqG36` | Completed source issues can become blocked again when they still have an open/unknown empty high-level dependency context. | valid | blocking | yes | fix-now | U001 | implemented | Done issues should remain ready even if raw high-level dependency context is incomplete; dependency blocker evaluation must not flip completed source readiness. | pending re-observation |
| I002 | codex_review_comment | C001 | review_feedback:cached-high-level-state | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py:168`, thread `PRRT_kwDOQ99OK86KqG3_` | `--no-github` cached high-level state reads issue-only `status` while sync stores high-level GitHub state under `github.state`. | valid | blocking | yes | fix-now | U001 | implemented | Cached closed epic/initiative dependencies must remain satisfied without live GitHub. | pending re-observation |
| I003 | codex_review_comment | C002 | review_feedback:cached-node-kind-schema | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py:171`, thread `PRRT_kwDOQ99OK86Kqu-H` | Cached high-level reader expects `kind`, but generated `index*.json` node schema uses `type`. | valid | blocking | yes | fix-now | U002 | implemented | Cached artifact reader must match generated schema and tests must use generated field shape. | pending re-observation |
| I004 | codex_review_comment | C002 | review_feedback:offline-sync-cache | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py:598`, thread `PRRT_kwDOQ99OK86Kqu-M` | `sync --no-github` does not pass cached high-level `github.state`, so offline sync rewrites closed high-level dependency as unknown blocker. | valid | blocking | yes | fix-now | U002 | implemented | Offline sync must preserve cached satisfied high-level dependencies. | pending re-observation |
| I005 | codex_review_comment | C002 | review_feedback:offline-active-set-cache | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py:532`, thread `PRRT_kwDOQ99OK86Kqu-P` | `active set --no-github` does not include cached high-level GitHub state, so offline activation is blocked by `empty_unknown`. | valid | blocking | yes | fix-now | U002 | implemented | Offline activation guard must use cached high-level state consistently. | pending re-observation |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<job_or_check_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: I001, I002
- Validity analysis: Both findings are valid. I001 identifies a completed-source readiness invariant violation. I002 identifies a cached high-level status lookup mismatch between sync artifact shape and no-github status resolution.
- Need-to-fix decision: yes.
- Root cause: The new high-level dependency path was added to readiness evaluation without excluding completed source issues from node-blocker application, and the cached status resolver for high-level nodes did not read the `github.state` field that sync writes for initiatives/epics.
- Options considered: ignore P2 comments as non-blocking; fix only tests; fix domain/application behavior and add regressions. The last option is required because both comments describe observable readiness regressions.
- Recommended disposition: fix-now via U001.
- Rationale: The issue scope is dependency readiness projection correctness; both findings are within scope and have small, testable fixes.
- Residual risk: none expected after focused tests, full local suite, and re-observation.

### C002

- Covered inventory IDs: I003, I004, I005
- Validity analysis: All three findings are valid. I003 identifies an artifact schema mismatch in the cache reader. I004 and I005 identify missing propagation of cached high-level state into offline sync and active-set readiness evaluation.
- Need-to-fix decision: yes.
- Root cause: U001 introduced a local cache reader for `deps check --no-github`, but it did not match the generated `index*.json` schema and was not shared by the other offline readiness paths.
- Options considered: fix only the field name; fix check/sync/active consistently with shared cache helper and regressions. The latter is required because the same readiness contract applies across offline workflows.
- Recommended disposition: fix-now via U002.
- Rationale: These are in-scope correctness issues for high-level dependency readiness projection and command guards.
- Residual risk: none expected after focused tests, full local suite, and re-observation.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260618t194321z-pr-repair-batch | I001, I002 | fix-now | blocking | `20260618t194411z-disc-pr-repair-unit-u001.md` | implemented | Added regressions for completed source issue with high-level blocker context and cached closed high-level dependency; updated domain/application logic; mirrored provider runtime; focused tests, validate, diff check, and broad unit / CLI runtime passed. | pending | pending re-observation |
| U002 | 20260618t194321z-pr-repair-batch | I003, I004, I005 | fix-now | blocking | `20260618t202851z-disc-pr-repair-unit-u002.md` | implemented | Read cached high-level state from generated `type` field and propagate it through offline check/sync/active-set paths; focused tests, validate, diff check, and broad unit / CLI runtime passed. | pending | pending re-observation |

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
- No required check failure remains.
- No non-required check failure remains unless the check is known optional or the user explicitly waived it; waived or optional non-required failures are recorded as residual risk.
- No blocking review feedback remains.
- No visible merge conflict or equivalent merge blocker remains.
- No `untriaged` inventory item remains.
- No unresolved `needs-human` item remains.
- No `blocking` item has an incomplete `fix-now` repair unit.
- Every `follow-up`, `no-action`, `covered-by`, `duplicate`, or `false-positive` item has rationale and residual risk where relevant.
- Observation limitation handling, resume metadata, trigger boundary, and new trigger approval status are recorded.
- Review-thread unresolved state is known, or any unresolved-thread limitation is explicitly waived and recorded as residual risk.
- `review-clean` is reported separately from `merge-prepared`; `review-clean: no` may still be `merge-prepared: yes` when all remaining items are triaged and non-blocking.
