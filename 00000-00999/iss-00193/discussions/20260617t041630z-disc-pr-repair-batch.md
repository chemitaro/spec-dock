---
種別: disc
ID: "disc-20260617t041630z-pr-repair-batch"
タイトル: "PR #194 repair batch"
状態: "proposed"
作成者: "codex"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: ["https://github.com/chemitaro/spec-dock/pull/194"]
authority: "proposed"
derived_from: ["/private/tmp/iss-00193-pr194-observation/result.json"]
reflected_to: []
---

# PR #194 repair batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/194
- PR number: 194
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00193-node-level-deps-add-remove
- Latest head SHA: d24bb64604410d1dee6eeef87718cf9b3d6a7697
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 194 --head-sha d24bb64604410d1dee6eeef87718cf9b3d6a7697 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --out /private/tmp/iss-00193-pr194-observation`
- Observation final JSON / evidence: `/private/tmp/iss-00193-pr194-observation/result.json`
- Observation status: `human_gate`; CI `passed`; review `unresolved`
- Trigger comment id: 4725778152
- Trigger created_at: 2026-06-17T04:00:31Z
- Trigger boundary: explicit `@codex review` posted by `wait_pr_observation.sh` for head `d24bb64604410d1dee6eeef87718cf9b3d6a7697`
- Resume metadata: N/A; observation reached terminal human_gate, not timeout
- New trigger approved: no
- Observation limitation: none
- Batch status: triaged; repair units required

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Raw node validation must consider future descendant issue expansion when empty containers are involved | I001, I002 | Validation currently protects mutation candidates but misses some structural invalid states involving empty containers and descendant-expanded issue edges; docs imply broader structural validation | U001 | Runtime repair required |
| C002 | Issue-local discussion draft filenames should follow catalog-compatible `<ts>-<kind>-<slug>.md` convention | I003 | Delegated draft evidence files were created with incomplete timestamp and non-catalog kind | U002 | Rename evidence files and update references |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | review_feedback | C001 | review_feedback:raw-validation | Review comment 3425508533 on `domain/deps.py` line 268 | Candidate raw validation can miss cycles that become compiled cycles after adding issues to an empty source container | valid | blocking | yes | fix-now | U001 | implemented | Containment-edge-aware raw validation added and covered by tests | Pending PR re-observation |
| I002 | review_feedback | C001 | review_feedback:validate-sync-contract | Review comment 3425508538 on `reference_deps.md` line 82 | `validate` / `sync` still accept existing raw node cycles if docs claim raw cycles are structural errors outside mutation | partially-valid | blocking | yes | fix-now | U001 | implemented | `validate` and `sync` preflight now run raw node validation | Pending PR re-observation |
| I003 | review_feedback | C002 | review_feedback:discussion-filename | Review comment 3425508539 on discussion draft filename | Design/plan discussion draft filenames do not match `discussions/rules.md` catalog form | valid | minor | yes | fix-now | U002 | implemented | Discussion drafts renamed and references updated; old-name grep is clean | Pending PR re-observation |

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
- Validity analysis: The finding is valid for mutation candidate coverage and partially valid for docs/validate scope. The issue's non-negotiable constraint is mutation-time rejection, but the docs now describe raw graph validity strongly enough that validate/sync should not silently pass pre-existing raw cycles.
- Need-to-fix decision: yes
- Root cause: Raw validation is a direct node graph check and compiled candidate validation only expands current issue sets. Empty source containers therefore can hide future compiled cycles through target descendants. Validation paths also keep using compiled issue graph loading only.
- Options considered:
  - Narrow docs to mutation-only. Rejected because the user explicitly chose fail-closed prevention for future child issue invalid states.
  - Add targeted descendant-expanded future self/cycle validation and wire raw graph validation into validation/sync paths. Recommended.
- Recommended disposition: fix-now
- Rationale: Both comments affect the central safety guarantee of iss-00193.
- Residual risk: Low after tests cover empty-container future cycle and validate/sync pre-existing raw cycle rejection.

### C002

- Covered inventory IDs: I003
- Validity analysis: Valid. `discussions/rules.md` asks for timestamp + catalog kind. Existing draft filenames are non-catalog.
- Need-to-fix decision: yes
- Root cause: Delegated discussion drafts used ad hoc incomplete timestamp and non-catalog kind prefixes.
- Options considered:
  - Leave as historical evidence. Rejected because PR review explicitly flagged catalog/tooling classification risk.
  - Rename and update references. Recommended.
- Recommended disposition: fix-now
- Rationale: Small, low-risk hygiene repair.
- Residual risk: Low after rename and reference search.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | disc-20260617t041630z-pr-repair-batch | I001, I002 | fix-now | blocking | `20260617t041631z-disc-pr-repair-unit-u001-raw-validation.md` | implemented | Added containment-edge raw validation plus validate/sync raw preflight; optional-port compatibility and validate error priority restored; full pytest passes | pending push / re-observation | Low; pending PR observation |
| U002 | disc-20260617t041630z-pr-repair-batch | I003 | fix-now | minor | `20260617t041632z-disc-pr-repair-unit-u002-discussion-filenames.md` | implemented | Renamed draft discussions and updated references; old-name grep clean | pending push / re-observation | Low; pending PR observation |

## Unit Discussion Plan

Create repair unit discussions before worker delegation. The worker must use the repair unit discussion, not raw findings, as the source of truth.

## Stop Conditions

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
