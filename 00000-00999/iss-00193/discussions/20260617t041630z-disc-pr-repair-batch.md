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
derived_from: ["/private/tmp/iss-00193-pr194-observation/result.json", "/private/tmp/iss-00193-pr194-snapshot-latest/result.json"]
reflected_to: []
---

# PR #194 repair batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/194
- PR number: 194
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00193-node-level-deps-add-remove
- Latest head SHA: d07cd68534953e4f47ff063704b3e8977766ca05
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 194 --head-sha d24bb64604410d1dee6eeef87718cf9b3d6a7697 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --out /private/tmp/iss-00193-pr194-observation`
- Observation final JSON / evidence: `/private/tmp/iss-00193-pr194-observation/result.json`
- Observation status: `human_gate`; CI `passed`; review `unresolved`
- Trigger comment id: 4725778152
- Trigger created_at: 2026-06-17T04:00:31Z
- Trigger boundary: explicit `@codex review` posted by `wait_pr_observation.sh` for head `d24bb64604410d1dee6eeef87718cf9b3d6a7697`
- Resume metadata: N/A; observation reached terminal human_gate, not timeout
- New trigger approved: no
- Observation limitation: none
- Latest observation command: `./.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh --repo chemitaro/spec-dock --pr 194 --head-sha d07cd68534953e4f47ff063704b3e8977766ca05 --out /private/tmp/iss-00193-pr194-snapshot-latest`
- Latest observation final JSON / evidence: `/private/tmp/iss-00193-pr194-snapshot-latest/result.json`
- Latest observation status: `human_gate`; CI `passed`; review `unresolved`
- Latest trigger comment id: 4726352168
- Latest trigger created_at: 2026-06-17T05:39:46Z
- Latest trigger boundary: inferred `@codex review` trigger for head `cdb61732741fb31f64e36318dffc623b6ccea6ee`
- Batch status: triaged; additional repair units required

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation. The batch separates validity from need-to-fix, groups related concerns, creates repair units when needed, and records residual risk for the final merge-prepared decision.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | Raw node validation must consider future descendant issue expansion when empty containers are involved | I001, I002 | Validation currently protects mutation candidates but misses some structural invalid states involving empty containers and descendant-expanded issue edges; docs imply broader structural validation | U001 | Runtime repair required |
| C002 | Issue-local discussion draft filenames should follow catalog-compatible `<ts>-<kind>-<slug>.md` convention | I003 | Delegated draft evidence files were created with incomplete timestamp and non-catalog kind | U002 | Rename evidence files and update references |
| C003 | Raw node validation must reject cycles through a target container when adding a dependency to a child node | I004 | Current containment edge model adds parent-to-child reachability but still misses child-to-container future expansion paths for target descendants | U003 | Runtime repair required |
| C004 | `deps check` must run raw dependency preflight before readiness is computed | I005 | `deps check` still validates only the compiled issue dependency map and can ignore empty-container raw cycles | U004 | Runtime repair required |
| C005 | Delete must block or scrub raw node dependencies that reference the deleted empty container subtree | I006 | Delete conflict/scrub logic is based on compiled issue edges, which can skip empty containers and leave dangling raw `depends_on` refs | U005 | Runtime repair required |
| C006 | CLI regression expectations must match `deps check` raw preflight error ordering | I007 | Existing `test_deps.py` assertions expected compiled issue-map errors, but U004 intentionally makes raw structural errors fail first | U006 | Test repair required |
| C007 | `active set` must reject pre-existing raw node dependency cycles before readiness succeeds | I008 | Active selection still validates only compiled issue dependencies and can miss raw-only cycles between empty containers | U007 | Runtime repair required |
| C008 | Delete must treat raw dependencies from deleted nodes to surviving nodes as boundary conflicts | I009 | U005 covered surviving raw refs into the deleted subtree, but outbound raw refs from the deleted subtree to survivors can bypass the no-force conflict guard | U008 | Runtime repair required |
| C009 | `doctor` must report raw node dependency validation failures | I010 | Doctor still validates only issue-level graph/deps and can report ok for repositories that `validate` rejects due to raw empty-container cycles | U009 | Runtime repair required |
| C010 | Delete raw dependency resolver failures must fail closed | I011 | Delete catches `load_node_dependency_resolutions` failures and falls back to literal node-id scan, losing GitHub number/scoped/URL raw-ref semantics | U010 | Runtime repair required |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | review_feedback | C001 | review_feedback:raw-validation | Review comment 3425508533 on `domain/deps.py` line 268 | Candidate raw validation can miss cycles that become compiled cycles after adding issues to an empty source container | valid | blocking | yes | fix-now | U001 | implemented | Containment-edge-aware raw validation added and covered by tests | Pending PR re-observation |
| I002 | review_feedback | C001 | review_feedback:validate-sync-contract | Review comment 3425508538 on `reference_deps.md` line 82 | `validate` / `sync` still accept existing raw node cycles if docs claim raw cycles are structural errors outside mutation | partially-valid | blocking | yes | fix-now | U001 | implemented | `validate` and `sync` preflight now run raw node validation | Pending PR re-observation |
| I003 | review_feedback | C002 | review_feedback:discussion-filename | Review comment 3425508539 on discussion draft filename | Design/plan discussion draft filenames do not match `discussions/rules.md` catalog form | valid | minor | yes | fix-now | U002 | implemented | Discussion drafts renamed and references updated; old-name grep is clean | Pending PR re-observation |
| I004 | review_feedback | C003 | review_feedback:raw-target-container-cycle | Review comment 3425775988 on `domain/deps.py` line 258 | Adding `init-00001 -> iss-00002` can be accepted when `iss-00002` is inside a container that already depends on `init-00001`, creating a future compiled cycle when `init-00001` later gains a child issue | valid | blocking | yes | fix-now | U003 | implemented | Source-descendant future expansion edge added to raw validation and covered by focused regression | Pending PR re-observation |
| I005 | review_feedback | C004 | review_feedback:deps-check-preflight | Review comment 3425775991 on `sync_state.py` line 477 | `deps check` can report readiness even when raw empty-container cycles would make `validate` / `sync` fail | valid | blocking | yes | fix-now | U004 | implemented | `deps check` now runs raw node validation preflight when topology reader exposes node resolutions | Pending PR re-observation |
| I006 | review_feedback | C005 | review_feedback:delete-raw-ref-scrub | Review comment 3425775994 on `mutate_deps.py` line 238 | Deleting an empty target container after node-level dependency add can leave unresolved raw `depends_on` references in source metadata | valid | blocking | yes | fix-now | U005 | implemented | Delete now detects surviving raw refs via resolved node dependencies, blocks without force, and scrubs with force | Pending PR re-observation |
| I007 | check_failure | C006 | check_failure:provider-tests | Provider CI run 27670570728 / job 81833757988 | `test_deps_self_dependency_fails` and `test_deps_descendant_dependency_fails` expected older compiled-graph stderr after U004 raw preflight changed fail-fast ordering | valid | blocking | yes | fix-now | U006 | implemented | Updated expectations to raw structural preflight stderr; focused and integrated local tests pass | Pending PR re-observation |
| I008 | review_feedback | C007 | review_feedback:active-set-raw-preflight | Review comment 3426282934 on `application/set_active.py` line 458 | `active set` can accept a scope whose empty-container raw dependencies form a cycle because it only checks compiled issue dependencies | valid | blocking | yes | fix-now | U007 | implemented | Added raw node dependency preflight to active selection before readiness succeeds | Pending PR re-observation |
| I009 | review_feedback | C008 | review_feedback:delete-outbound-raw-conflict | Review comment 3426282937 on `application/delete_node.py` line 332 | Deleting a subtree can skip raw outbound dependencies from deleted empty nodes to surviving empty containers, unlike existing boundary dependency conflict semantics | valid | blocking | yes | fix-now | U008 | implemented | Delete boundary conflict detection now includes raw outbound refs resolved by topology reader | Pending PR re-observation |
| I010 | review_feedback | C009 | review_feedback:doctor-raw-preflight | Review comment 3426282941 on `application/doctor.py` line 80 | `doctor` can report ok for raw empty-container dependency cycles because it does not run raw node dependency validation | valid | blocking | yes | fix-now | U009 | implemented | Doctor now reports raw node dependency validation findings | Pending PR re-observation |
| I011 | review_feedback | C010 | review_feedback:delete-raw-resolution-fail-closed | Review comment 3426476954 on `application/delete_node.py` line 675 | If raw dependency resolution fails globally, delete falls back to literal node-id scan and may miss surviving raw refs expressed as GitHub numbers, scoped refs, or URLs | valid | blocking | yes | fix-now | U010 | implemented | Delete now fails closed on raw dependency resolution failure before local mutation | Pending PR re-observation |

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

### C003

- Covered inventory IDs: I004
- Validity analysis: Valid. A target issue can be inside a container that already depends on the source container; the raw validation must account for the future issue-level expansion edge from the target descendant back through its container.
- Need-to-fix decision: yes
- Root cause: Containment reachability was modeled in only one direction for raw validation. That protects some empty-container future states but not the target-descendant/container path identified by review.
- Options considered:
  - Treat this as a docs limitation. Rejected because the user explicitly chose fail-closed future-cycle prevention.
  - Extend raw validation to include the relevant container/descendant expansion path and add a regression. Recommended.
- Recommended disposition: fix-now
- Rationale: This is the same safety invariant as Option A and blocks merge-prepared status.
- Residual risk: Low after focused domain/CLI tests cover the example shape.

### C004

- Covered inventory IDs: I005
- Validity analysis: Valid. `deps check` is a readiness surface and should not report a target ready when structural raw dependency validation fails.
- Need-to-fix decision: yes
- Root cause: `deps check` consumes compiled issue dependencies only, so empty-container raw edges can disappear before readiness computation.
- Options considered:
  - Leave `deps check` as issue-level only. Rejected because readiness output would contradict validate/sync structural validity.
  - Run raw node validation preflight when the topology reader exposes raw node dependency resolutions. Recommended.
- Recommended disposition: fix-now
- Rationale: Users rely on `deps check` as an actionable readiness gate.
- Residual risk: Low after application/CLI regression covers empty-container raw cycle.

### C005

- Covered inventory IDs: I006
- Validity analysis: Valid. Node-level dependency mutation can introduce raw refs to empty containers; delete must not leave dangling metadata that only fails after the destructive local mutation.
- Need-to-fix decision: yes
- Root cause: Delete conflict/scrub logic uses compiled issue dependencies and therefore has no edge to inspect when the referenced target subtree has no issues.
- Options considered:
  - Block deletion when any raw `depends_on` references the target subtree. Safe but may be stricter.
  - Scrub direct raw refs as part of confirmed recursive delete. Lower friction if existing delete semantics already scrub issue-level references.
  - Recommended: match existing delete semantics for dependency cleanup where possible, but fail before destructive delete if raw refs cannot be cleaned.
- Recommended disposition: fix-now
- Rationale: No dangling raw dependency refs may remain after successful delete.
- Residual risk: Medium until implementation confirms the existing delete transaction/rollback shape.

### C006

- Covered inventory IDs: I007
- Validity analysis: Valid. The CI failure came from stale test expectations, not a runtime behavior defect. U004 intentionally makes `deps check` run raw structural validation before compiled issue dependency readiness.
- Need-to-fix decision: yes
- Root cause: `tests/cli_runtime/test_deps.py` still asserted compiled graph error strings for raw self/descendant invalid metadata.
- Options considered:
  - Reorder runtime validation to preserve older stderr. Rejected because U004 is explicitly a fail-fast raw preflight repair.
  - Update tests to assert the new raw structural stderr. Recommended.
- Recommended disposition: fix-now
- Rationale: Provider CI must reflect the accepted raw preflight contract.
- Residual risk: Low after focused and integrated test bundle pass.

### C007

- Covered inventory IDs: I008
- Validity analysis: Valid. `active set` is a readiness gate and must not mark a scope active when existing raw node dependencies already violate the Option A cycle-prevention invariant.
- Need-to-fix decision: yes
- Root cause: `active set` loads and validates compiled issue dependencies only; raw dependencies between empty containers can disappear before the cycle check.
- Options considered:
  - Leave `active set` as issue-only. Rejected because it would allow active context to start from a state that `validate` / `sync` reject.
  - Reuse the raw dependency resolution reader and run `validate_raw_node_dependency_graph` before readiness succeeds. Recommended.
- Recommended disposition: fix-now
- Rationale: Active context is a high-trust execution entrypoint; it must share structural raw dependency preflight with validate/sync/deps check.
- Residual risk: Low after a focused active-set regression covers empty-container raw cycle rejection.

### C008

- Covered inventory IDs: I009
- Validity analysis: Valid. Existing delete semantics block dependency edges crossing the deleted subtree boundary unless `--force`; raw outbound dependencies from deleted nodes to surviving nodes are the same boundary condition even when no issues exist.
- Need-to-fix decision: yes
- Root cause: U005 added surviving-source raw refs into the deleted subtree, but the raw boundary collector still ignores deleted-source refs that resolve outside the subtree.
- Options considered:
  - Ignore outbound raw refs because the source metadata is deleted. Rejected because no-force delete would no longer protect users from dependency boundary changes.
  - Add raw outbound refs to the dependency conflict set, while force deletion may proceed because the source metadata is removed with the subtree. Recommended.
- Recommended disposition: fix-now
- Rationale: This aligns raw node dependencies with existing compiled issue boundary conflict behavior.
- Residual risk: Low after CLI regressions cover no-force block and force success for deleted-source raw refs to surviving empty containers.

### C009

- Covered inventory IDs: I010
- Validity analysis: Valid. `doctor` should surface structural repository problems; reporting ok for a raw cycle that `validate` rejects is misleading.
- Need-to-fix decision: yes
- Root cause: `doctor` uses graph / issue dependency validation without raw node dependency resolution preflight.
- Options considered:
  - Keep `doctor` lightweight and rely on `validate`. Rejected because users expect doctor to detect inconsistent local state.
  - Run raw node dependency validation when the topology reader exposes raw resolutions, reporting failures as findings without changing unrelated doctor checks. Recommended.
- Recommended disposition: fix-now
- Rationale: This brings doctor into the same structural invariant family as validate/sync/deps check/active set.
- Residual risk: Low after CLI regression verifies doctor reports raw empty-container cycles.

### C010

- Covered inventory IDs: I011
- Validity analysis: Valid. Resolver failure means delete cannot know whether raw refs using numeric, scoped, or URL forms cross the deleted subtree boundary.
- Need-to-fix decision: yes
- Root cause: `_collect_surviving_raw_node_dependency_refs` discards resolver exceptions and continues with a literal node-id fallback.
- Options considered:
  - Keep fallback after resolver failure. Rejected because it is fail-open for non-literal raw refs.
  - Propagate a dependency topology load failure and stop before local delete mutation. Recommended.
- Recommended disposition: fix-now
- Rationale: Delete is destructive; unresolved dependency topology must not allow no-force success or force with dangling surviving metadata.
- Residual risk: Low after regression proves resolver exceptions return a non-ok preflight result and skip delete/scrub mutation.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | disc-20260617t041630z-pr-repair-batch | I001, I002 | fix-now | blocking | `20260617t041631z-disc-pr-repair-unit-u001-raw-validation.md` | implemented | Added containment-edge raw validation plus validate/sync raw preflight; optional-port compatibility and validate error priority restored; full pytest passes | pending push / re-observation | Low; pending PR observation |
| U002 | disc-20260617t041630z-pr-repair-batch | I003 | fix-now | minor | `20260617t041632z-disc-pr-repair-unit-u002-discussion-filenames.md` | implemented | Renamed draft discussions and updated references; old-name grep clean | pending push / re-observation | Low; pending PR observation |
| U003 | disc-20260617t041630z-pr-repair-batch | I004 | fix-now | blocking | `20260617t053300z-disc-pr-repair-unit-u003-target-container-cycle.md` | implemented | Extended raw validation to reject target-descendant/container future cycles and added focused domain regression | pending push / re-observation | Low; pending PR observation |
| U004 | disc-20260617t041630z-pr-repair-batch | I005 | fix-now | blocking | `20260617t053301z-disc-pr-repair-unit-u004-deps-check-preflight.md` | implemented | Added raw node dependency preflight to `deps check`; optional-port compatibility preserved | pending push / re-observation | Low; pending PR observation |
| U005 | disc-20260617t041630z-pr-repair-batch | I006 | fix-now | blocking | `20260617t053302z-disc-pr-repair-unit-u005-delete-raw-ref-cleanup.md` | implemented | Delete raw-ref detection now uses `load_node_dependency_resolutions` when available, scrubs exact resolver raw refs, and falls back to direct node-id conflict plus heuristic scrub | pending push / re-observation | Low; pending PR observation |
| U006 | disc-20260617t041630z-pr-repair-batch | I007 | fix-now | blocking | N/A | implemented | Updated `tests/cli_runtime/test_deps.py` expectations for raw preflight stderr | pending push / re-observation | Low; pending PR observation |
| U007 | disc-20260617t041630z-pr-repair-batch | I008 | fix-now | blocking | `20260617t060000z-disc-pr-repair-unit-u007-active-set-raw-preflight.md` | implemented | Added raw node dependency validation preflight to `active set`; optional-port compatibility preserved | pending push / re-observation | Low; focused and integrated tests pass |
| U008 | disc-20260617t041630z-pr-repair-batch | I009 | fix-now | blocking | `20260617t060001z-disc-pr-repair-unit-u008-delete-outbound-raw-conflicts.md` | implemented | Added raw outbound deleted-source to surviving-target dependency conflicts; no-force blocks, force proceeds because source metadata is deleted | pending push / re-observation | Low; focused and integrated tests pass |
| U009 | disc-20260617t041630z-pr-repair-batch | I010 | fix-now | blocking | `20260617t060002z-disc-pr-repair-unit-u009-doctor-raw-preflight.md` | implemented | Added raw node dependency validation finding to `doctor` | pending push / re-observation | Low; focused and integrated tests pass |
| U010 | disc-20260617t041630z-pr-repair-batch | I011 | fix-now | blocking | `20260617t080000z-disc-pr-repair-unit-u010-delete-raw-resolution-fail-closed.md` | implemented | Return dependency topology load failure when raw dependency resolution fails during delete preflight | pending push / re-observation | Low; focused and integrated tests pass |

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
