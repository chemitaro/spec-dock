---
種別: pr-repair-batch
ID: "20260617t043527z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
authority: "proposed"
derived_from:
  - "https://github.com/chemitaro/spec-dock/pull/195"
  - "/private/tmp/pr-195-observation/result.json"
  - "/private/tmp/pr-195-observation-b04c0b1d/result.json"
  - "/private/tmp/pr-195-observation-bb0b751a/result.json"
reflected_to: []
---

# 20260617t043527z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/195
- PR number: 195
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00188-prevent-duplicate-discussion-timestamp-slots
- Latest head SHA: bb0b751a58b7d86f9f01feff89e5d0e2c2333bfa
- Initial observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 195 --head-sha 821eb10993b299e3daaa0dba8496c88e1062c034 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --body-mode trigger-window-truncated --out /private/tmp/pr-195-observation`
- Initial observation final JSON / evidence: `/private/tmp/pr-195-observation/result.json`
- Initial observation status: failed; `recommended_next_action=fix_ci`; `status_reason=ci_failed`
- Initial trigger comment id: 4725934579
- Initial trigger created_at: 2026-06-17T04:24:37Z
- Re-observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 195 --head-sha b04c0b1da21f23adc50859ed7c32c2d029f28765 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --body-mode trigger-window-truncated --out /private/tmp/pr-195-observation-b04c0b1d`
- Re-observation final JSON / evidence: `/private/tmp/pr-195-observation-b04c0b1d/result.json`
- Re-observation status: human_gate; `recommended_next_action=address_review_feedback`; CI passed; 3 current-trigger unresolved review threads
- Re-observation trigger comment id: 4726082469
- Re-observation trigger created_at: 2026-06-17T04:48:32Z
- Second re-observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 195 --head-sha bb0b751a58b7d86f9f01feff89e5d0e2c2333bfa --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --body-mode trigger-window-truncated --out /private/tmp/pr-195-observation-bb0b751a`
- Second re-observation final JSON / evidence: `/private/tmp/pr-195-observation-bb0b751a/result.json`
- Second re-observation status: human_gate; `recommended_next_action=address_review_feedback`; CI passed; 3 current-trigger unresolved review threads
- Second re-observation trigger comment id: 4726406116
- Second re-observation trigger created_at: 2026-06-17T05:35:32Z
- Trigger boundary: explicit `@codex review` posted by wait script for each observed head SHA
- Resume metadata: not applicable; neither observation ended by timeout
- New trigger approved: yes for latest pushed head; no resume boundary was crossed
- Observation limitation: none reported; review thread state is available and unresolved
- Batch status: second-review-repair-implemented

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | provider-tests layer import failure | I001 | `commands/new.py` imports `domain.discussion_docs`, violating shell layer rule that `commands/*` must not import domain/infra/app directly | U001 | Local focused tests did not include `test_runtime_shell_s11.py`; CI full provider suite caught it |
| C002 | allocated timestamp/date placeholder drift | I002 | `plan_discussion_doc` computes `today` before the retry allocator can advance to another UTC day | U002 | Latest Codex review P2 on `create_node.py` |
| C003 | skill-local repair batch template identity drift | I003 | `github-pr-merge-preparer` still names the skill-local template as the generated artifact source even though `new doc pr-repair-batch` now owns identity/front matter | U003 | Latest Codex review P2 on `github-pr-merge-preparer/SKILL.md` |
| C004 | bare hyphenated doc-type validation gap | I004 | malformed-intent detection catches `pr-repair-batch-*` / `pr-repair-batch_*` but not exact `pr-repair-batch.md` | U004 | Latest Codex review P2 on `discussion_docs.py` |
| C005 | delegated diff guard rejects generated `pr-repair-batch` docs | I005 | `delegated_authoring.py` has its own hard-coded discussion filename regex that omits `pr-repair-batch` | U005 | Second Codex review P2 on `discussion_docs.py` |
| C006 | shipped README catalog omits `pr-repair-batch` | I006 | installed README catalog lists older discussion templates/doc types only | U006 | Second Codex review P3 on `commands/new.py` |
| C007 | suffix fallback may switch to later occupied timestamp family | I007 | wait/retry loop updates fallback timestamp to an occupied later timestamp before finding a free standard slot | U007 | Second Codex review P2 on `create_node.py` |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | CI check | C001 | check_failure:provider-tests | `gh run view 27665658157 --log-failed`; failed test `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` directly imports `domain.discussion_docs`, which is forbidden for the command shell layer | valid | blocking | yes | fix-now | U001 | implemented | The layer contract is explicit and the failure is reproducible from CI logs. Local repair verification passed; re-observation pending. | pending PR re-observation |
| I002 | Codex review | C002 | review_feedback:body-date-after-timestamp-retry | `/private/tmp/pr-195-observation-b04c0b1d/result.json`; comment id 3425692862; thread `PRRT_kwDOQ99OK86KGvVm`; path `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` | If timestamp retry crosses UTC midnight, generated ID/path can be one day later than rendered date placeholders. | valid | blocking | yes | fix-now | U002 | implemented | The code path intentionally waits and retries timestamp allocation; rendered body dates now derive from the allocated doc id. | pending PR re-observation |
| I003 | Codex review | C003 | review_feedback:repair-batch-template-identity | `/private/tmp/pr-195-observation-b04c0b1d/result.json`; comment id 3425692868; thread `PRRT_kwDOQ99OK86KGvVo`; path `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` | Workflow guidance can still cause a generated `pr-repair-batch` identity to be overwritten or mixed with the stale skill-local `disc` template. | valid | blocking | yes | fix-now | U003 | implemented | Guidance now states generated file owns front matter identity; skill-local template is body-section scaffold only. | pending PR re-observation |
| I004 | Codex review | C004 | review_feedback:bare-hyphenated-doc-type-validation | `/private/tmp/pr-195-observation-b04c0b1d/result.json`; comment id 3425692872; thread `PRRT_kwDOQ99OK86KGvVr`; path `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py` | A bare `pr-repair-batch.md` in a `discussions/` directory is ignored by validation instead of failing as malformed intent. | valid | blocking | yes | fix-now | U004 | implemented | Exact bare known doc-type stems are now malformed candidates. | pending PR re-observation |
| I005 | Codex review | C005 | review_feedback:delegated-diff-guard-pr-repair-batch | `/private/tmp/pr-195-observation-bb0b751a/result.json`; comment id 3425870058; thread `PRRT_kwDOQ99OK86KHORK`; path `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py` | `evaluate_diff_guard` can reject runtime-generated `pr-repair-batch` discussion docs as `discussion_name_noncompliant`. | valid | blocking | yes | fix-now | U005 | implemented | Delegated diff guard now uses the shared discussion parser/catalog for creatable discussion doc names. | pending PR re-observation |
| I006 | Codex review | C006 | review_feedback:shipped-readme-pr-repair-batch-catalog | `/private/tmp/pr-195-observation-bb0b751a/result.json`; comment id 3425870061; thread `PRRT_kwDOQ99OK86KHORN`; path `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` | Installed user-facing READMEs omit `pr-repair-batch` from discussion catalog lists. | valid | material-follow-up | yes | fix-now | U006 | implemented | Shipped README catalog surfaces now mention `pr-repair-batch` and the `new doc pr-repair-batch` path. | pending PR re-observation |
| I007 | Codex review | C007 | review_feedback:suffix-fallback-original-timestamp | `/private/tmp/pr-195-observation-bb0b751a/result.json`; comment id 3425870063; thread `PRRT_kwDOQ99OK86KHORP`; path `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` | If retry sees a later occupied timestamp, suffix fallback can exhaust in the later family instead of the original colliding family. | valid | blocking | yes | fix-now | U007 | implemented | Retry now falls back to the original collision family unless a later free standard slot is found. | pending PR re-observation |

## Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<job_or_check_name>` / `review_feedback:<topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `timeout` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### C001

- Covered inventory IDs: I001
- Validity analysis: valid. `test_runtime_shell_s11.py` enforces that `commands/*` remain thin and do not directly import `domain`, `infra`, or `app`.
- Need-to-fix decision: yes.
- Root cause: S02/S04 reused the shared discussion catalog in `commands/new.py` for help text, but placed that import directly in the command layer instead of passing the creatable doc type list through an application/contract boundary or duplicating a presentation-safe constant.
- Options considered:
  - Move help text derivation back to local command-layer constant, accepting drift risk.
  - Expose a command-safe helper/constant outside `domain` and keep shared catalog semantics.
  - Update the structural test to allow this domain import.
- Recommended disposition: fix-now via U001.
- Rationale: The CI failure is blocking and the structural rule should remain intact.
- Residual risk: none expected if focused structural test and relevant new-doc tests pass.

### C002

- Covered inventory IDs: I002
- Validity analysis: valid. The allocator may wait and retry after a collision; if the retry crosses UTC midnight, date placeholders derived before allocation no longer correspond to the allocated timestamp.
- Need-to-fix decision: yes.
- Root cause: body placeholder context computes `today` from the original call instant instead of deriving it from `planned.doc_id` / allocated timestamp.
- Options considered:
  - Keep current behavior and treat cross-midnight as negligible.
  - Recompute rendered date from the allocated timestamp after `plan_discussion_doc`.
  - Return a date from the allocator in a broader API change.
- Recommended disposition: fix-now via U002.
- Rationale: Recomputing from the allocated timestamp is narrow and preserves public interfaces.
- Residual risk: low after focused regression test.

### C003

- Covered inventory IDs: I003
- Validity analysis: valid. `new doc pr-repair-batch` now owns front matter identity, but the skill still tells the workflow to create/update from a skill-local template that uses `disc` placeholders.
- Need-to-fix decision: yes.
- Root cause: #188 updated the generated artifact path but left the skill-local template identity semantics stale.
- Options considered:
  - Convert the skill-local template to a `pr-repair-batch` template.
  - Keep the template as body-only sections and explicitly forbid copying its front matter over generated identity.
  - Remove the skill-local template reference from normal writable-scope flow.
- Recommended disposition: fix-now via U003, using a minimal guidance/template update that preserves generated front matter and limits the skill-local template to section/body scaffolding.
- Rationale: This avoids reintroducing manual or stale identity ownership.
- Residual risk: low after `rg` inspection and asset parity checks.

### C004

- Covered inventory IDs: I004
- Validity analysis: valid. Exact `pr-repair-batch.md` is an obvious malformed intent file for the newly creatable doc type but is not caught by the current prefix/separator detection.
- Need-to-fix decision: yes.
- Root cause: malformed-intent detection only recognizes type stems followed by `-` or `_`.
- Options considered:
  - Catch exact stems for all known discussion doc types.
  - Catch exact stems only for hyphenated doc types.
  - Leave exact stems ignored.
- Recommended disposition: fix-now via U004, adding exact-stem detection for known doc type tokens without changing valid timestamp grammar.
- Rationale: This is the narrow fail-closed behavior requested by the review.
- Residual risk: low after validation regression tests.

### C005

- Covered inventory IDs: I005
- Validity analysis: valid. The new doc type was added to runtime creation and validation, but delegated authoring has a separate filename guard.
- Need-to-fix decision: yes.
- Root cause: duplicated filename grammar in `domain/delegated_authoring.py`.
- Options considered:
  - Add `pr-repair-batch` to the duplicated regex.
  - Reuse the shared discussion doc parser/catalog where possible.
- Recommended disposition: fix-now via U005.
- Rationale: A generated artifact must not fail a shipped diff guard.
- Residual risk: low after diff-guard regression tests.

### C006

- Covered inventory IDs: I006
- Validity analysis: valid. The installed READMEs are user-facing catalog surfaces and now stale.
- Need-to-fix decision: yes.
- Root cause: S02 updated CLI/catalog behavior but did not update both shipped README catalog lists.
- Options considered:
  - Defer as follow-up because P3.
  - Fix now as small catalog parity doc update.
- Recommended disposition: fix-now via U006.
- Rationale: This is small, shipped, and prevents users from missing the supported runtime path.
- Residual risk: low after README/catalog inspection.

### C007

- Covered inventory IDs: I007
- Validity analysis: valid. The fallback timestamp family can be overwritten by a later occupied timestamp observed during retry.
- Need-to-fix decision: yes.
- Root cause: wait/retry state tracks the last observed occupied timestamp rather than the original fallback timestamp.
- Options considered:
  - Keep current behavior.
  - Preserve original fallback timestamp while allowing a later free standard slot to win.
- Recommended disposition: fix-now via U007.
- Rationale: Suffix fallback is explicitly retained as safety fallback; it should not become less reliable under busy later seconds.
- Residual risk: low after focused suffix exhaustion regression.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | `20260617t043527z-pr-repair-batch` | I001 | fix-now | blocking | `20260617t043551z-disc-pr-repair-unit-u001-provider-tests-layer-import.md` | implemented | Remove forbidden command-layer domain import while preserving `pr-repair-batch` help/catalog behavior; run structural and focused new-doc tests. | pending PR re-observation | pending PR re-observation |
| U002 | `20260617t043527z-pr-repair-batch` | I002 | fix-now | blocking | `20260617t050751z-disc-pr-repair-unit-u002-body-date-after-timestamp-retry.md` | implemented | Derive rendered date placeholders from the allocated timestamp after retry; add regression test for UTC day rollover. | pending PR re-observation | pending PR re-observation |
| U003 | `20260617t043527z-pr-repair-batch` | I003 | fix-now | blocking | `20260617t050753z-disc-pr-repair-unit-u003-repair-batch-template-identity.md` | implemented | Update shipped merge-preparer guidance/template semantics so generated `pr-repair-batch` front matter is preserved. | pending PR re-observation | pending PR re-observation |
| U004 | `20260617t043527z-pr-repair-batch` | I004 | fix-now | blocking | `20260617t050752z-disc-pr-repair-unit-u004-bare-hyphenated-doc-type-validation.md` | implemented | Reject exact bare doc-type stems such as `pr-repair-batch.md`; add validation regression tests. | pending PR re-observation | pending PR re-observation |
| U005 | `20260617t043527z-pr-repair-batch` | I005 | fix-now | blocking | `20260617t055224z-disc-pr-repair-unit-u005-delegated-authoring-pr-repair-batch-guard.md` | implemented | Ensure delegated diff guard accepts generated `pr-repair-batch` filenames; prefer shared parser/catalog or add focused parity test. | pending PR re-observation | pending PR re-observation |
| U006 | `20260617t043527z-pr-repair-batch` | I006 | fix-now | material-follow-up | `20260617t055225z-disc-pr-repair-unit-u006-shipped-readme-pr-repair-batch-catalog.md` | implemented | Update shipped README catalog lists for `pr-repair-batch`. | pending PR re-observation | pending PR re-observation |
| U007 | `20260617t043527z-pr-repair-batch` | I007 | fix-now | blocking | `20260617t055226z-disc-pr-repair-unit-u007-suffix-fallback-original-timestamp.md` | implemented | Preserve original fallback timestamp family while allowing later free standard slots. | pending PR re-observation | pending PR re-observation |

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
