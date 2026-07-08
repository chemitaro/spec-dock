---
種別: pr-repair-batch
ID: "20260708t192858z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["iss-00309"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260708t192858z-pr-repair-batch PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/310
- PR number: 310
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign
- Latest head SHA before repair: `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7`
- Observation command: `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- Observation final JSON / evidence: local PR observation snapshot for PR #310 head `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7`
- Observation status: `human_gate`
- Trigger comment id: recorded by PR observation snapshot
- Trigger created_at: recorded by PR observation snapshot
- Trigger boundary: fixed-endpoint Codex PR review for latest pushed head
- Resume metadata: none
- New trigger approved: no
- Observation limitation: 7 P1 review findings blocked merge-prepared state; required CI passed.
- Batch status: implemented locally; pending repair commit, push, and re-observation.

## Batch Purpose

Repair the P1 findings raised after the report-only PR update, without changing
the adopted planning output decision for this Issue.

The adopted authoring output remains the ChatGPT Use direct ZIP route because it
left a locally inspectable ZIP, listing, digest, and staged file evidence. The
script route remains rejected for this Issue because the claimed ZIP did not
materialize locally and therefore could not be inspected or adopted.

## Persistence Policy

This file is for blocking repair work.

Use this repo-persistent batch when:

- `P0`/`P1` review findings exist.
- Required GitHub Actions CI failures exist.
- Merge blockers exist.
- Blocking observation limitations require repair or human-gate tracking.
- Branch mutation is already required for blocking repair and non-blocking
  findings can be recorded in the same commit without causing an extra CI run.

Do not update this batch solely to record terminal `P2`/`P3` findings after the
latest pushed head has no blockers. Record terminal `P2`/`P3` findings in the
final merge-prepared report instead, unless the user explicitly requests
separate follow-up tracking outside the current PR branch.

## Observation Batch Summary

| field | value |
| --- | --- |
| latest_head_sha | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` before repair |
| observation_status | `human_gate` |
| required_ci_status | passed |
| review_status | 7 P1 findings |
| p0_count | 0 |
| p1_count | 7 |
| p2_count | 0 |
| p3_count | 0 |
| required_ci_failure_count | 0 |
| merge_blocker_count | 7 |
| blocking_family_count | 7 |
| non_blocking_family_count | 0 |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | no |
| merge_prepared_candidate | no |

## Raw Intake Inventory

| item_id | source_type | source_id | reported_priority | path | line | raw_summary | evidence_type | current_head_sha | family_id | intake_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | review | candidate-pack-digest-coverage | P1 | `candidate_contract.py` | 435 | `tree_digest()` silently skipped symlinks / unsupported entries. | contract | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | F001 | triaged |
| R002 | review | authoring-metadata-schema-validation | P1 | `zip_contract.py` | 300 | Required JSON metadata that parsed as non-object could still pass. | contract | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | F002 | triaged |
| R003 | review | backend-prompt-pack-symlink-boundary | P1 | `backend_invoke.py` | 186 | `--prompt-pack` symlink roots or ancestors could pass after `resolve()`. | contract | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | F003 | triaged |
| R004 | review | authoring-zip-entry-uniqueness | P1 | `zip_contract.py` | 126 | Duplicate ZIP relative entries could pass review. | contract | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | F004 | triaged |
| R005 | review | candidate-index-payload-identity | P1 | `candidate_contract.py` | 249 | Index identity could differ from internal `candidate.json`. | contract | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | F005 | triaged |
| R006 | review | draft-artifact-symlink-boundary | P1 | `draft_adoption_contract.py` | 510 | Artifact paths could follow symlink ancestors under `issue_dir`. | contract | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | F006 | triaged |
| R007 | review | prompt-pack-preflight-hash-consistency | P1 | `pack_prepare.py` | 232 | `source_manifest_hash` could disagree with `source_hashes`. | contract | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | F007 | triaged |

## Concern Family Catalog

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | candidate_digest.closed_world | Candidate pack digest must fail closed on symlink / unsupported entries | yes | Candidate review digest covers every entry or rejects the pack. | R001 | P1 | P1 | yes | fix-now | U001 | implemented |
| F002 | zip_metadata.object_schema | Required metadata JSON must be objects | yes | Metadata that is JSON but not an object is a schema failure. | R002 | P1 | P1 | yes | fix-now | U002 | implemented |
| F003 | backend_prompt_pack.lexical_symlink_boundary | Prompt pack path must not traverse symlink components | yes | Backend invocation only accepts non-symlink prompt pack roots and in-repo ancestors. | R003 | P1 | P1 | yes | fix-now | U003 | implemented |
| F004 | zip_entries.unique_relative_names | ZIP relative entry names are unique | yes | Duplicate entries cannot shadow reviewed content. | R004 | P1 | P1 | yes | fix-now | U004 | implemented |
| F005 | candidate_identity.index_payload_consistency | Candidate index and payload identity match | yes | `candidate_id`, `title`, and `slug` in index and payload are identical. | R005 | P1 | P1 | yes | fix-now | U005 | implemented |
| F006 | draft_paths.no_symlink_components | Draft and selected section artifact paths do not cross symlink ancestors | yes | Every path component under `issue_dir` is checked before reading. | R006 | P1 | P1 | yes | fix-now | U006 | implemented |
| F007 | preflight_source_manifest.consistent_hash | Preflight source manifest hash matches source hashes | yes | `source_manifest_hash` is recomputed from filtered `source_hashes`. | R007 | P1 | P1 | yes | fix-now | U007 | implemented |

## Per-Family Analysis

All seven findings are valid P1 contract gaps in the authoring evidence lane.
They share the same safety objective: ChatGPT / Oracle outputs remain
evidence-only until local runtime validation proves path safety, metadata shape,
candidate identity, digest coverage, and source freshness. Each family is
implemented as a narrow runtime guard plus regression coverage in
`tests/cli_runtime/test_authoring.py`.

## Blocking Repair Queue

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260708t192858z-pr-repair-batch | F001 | R001 | P1 | yes | fix-now | N/A | implemented | Make `tree_digest()` reject symlink / unsupported entries and carry findings. | `test_authoring_validate_epic_issue_candidates_negative_contracts` | pending | pending | low |
| U002 | 20260708t192858z-pr-repair-batch | F002 | R002 | P1 | yes | fix-now | N/A | implemented | Require metadata JSON objects and classify as fail. | `test_authoring_pack_compatibility_review_fails_non_object_metadata` | pending | pending | low |
| U003 | 20260708t192858z-pr-repair-batch | F003 | R003 | P1 | yes | fix-now | N/A | implemented | Reject symlink prompt pack path components while preserving legacy prompt-only wrapper. | `test_authoring_backend_invoke_rejects_symlink_prompt_pack_path`; legacy prompt-only test | pending | pending | low |
| U004 | 20260708t192858z-pr-repair-batch | F004 | R004 | P1 | yes | fix-now | N/A | implemented | Track duplicate ZIP relative names during review. | `test_authoring_pack_compatibility_review_rejects_duplicate_zip_entries` | pending | pending | low |
| U005 | 20260708t192858z-pr-repair-batch | F005 | R005 | P1 | yes | fix-now | N/A | implemented | Compare index `candidate_id` / `title` / `slug` with payload values. | `candidate-id-mismatch` negative contract | pending | pending | low |
| U006 | 20260708t192858z-pr-repair-batch | F006 | R006 | P1 | yes | fix-now | N/A | implemented | Check every draft / section-fill path component for symlink before reading. | `symlink-ancestor` draft and selected skeleton negatives | pending | pending | low |
| U007 | 20260708t192858z-pr-repair-batch | F007 | R007 | P1 | yes | fix-now | N/A | implemented | Recompute manifest hash from filtered `source_hashes` in pack prepare. | `test_authoring_pack_prepare_rejects_inconsistent_source_manifest_hash` | pending | pending | low |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

None.

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G001 | F001-F007 | `uv run ruff check ... tests/cli_runtime/test_authoring.py` | pass | R001-R007 | yes |
| G002 | F001-F007 | `uv run pytest tests/cli_runtime/test_authoring.py -k "duplicate_zip_entries or non_object_metadata or documented_source_manifest_hash_flag or epic_issue_candidates_negative_contracts or issue_draft_adoption_negative_matrix or selected_skeleton_fill_negative_matrix or inconsistent_source_manifest_hash or dogfood_runtime_path_smoke or symlink_prompt_pack_path"` | pass | R001-R007 | yes |
| G003 | F001-F007 | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | R001-R007 plus surrounding authoring contracts | yes |

## Re-observation Plan

- Latest head before repair: `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7`
- Expected head after repair: pending commit
- Re-observation command: `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- Trigger mode: post-once / resume
- Resume trigger comment id: pending after push
- Resume trigger created_at: pending after push
- New trigger approved: yes / no
- Re-observation required because: the branch is mutated to repair P1 findings.
- Re-observation skipped because:

## Loop Control

| iteration | head_sha | observation_status | family_id | action_taken | fix_commit | reappeared_after_fix | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `2a6d951438f4c6cc0ae9db0f738981b2ed1b97b7` | `human_gate` | F001-F007 | Implement runtime guards, tests, fixture update, and dogfood mirror sync | pending | no | commit, push, re-observe |
| 2 | `f8aeb4ef611540ae0cc17f06781b5c76387be558` | `timeout` with Provider CI still running, review unresolved | F008-F011 | Implement second review batch: required metadata field validation, selected-skeleton review gate, draft pack digest binding, and null `authorized_profile` structural scan handling | pending | pending | commit, push, re-observe |

## Second Review Batch Addendum

The resumed PR observation for head `f8aeb4ef611540ae0cc17f06781b5c76387be558`
reported four additional P1 findings and one P2. The P2
`backend-invoke.symlink-boundary` is non-blocking and is not repaired in this
batch. The four P1 findings were implemented locally:

| item_id | source_id | priority | family_id | summary | local disposition |
| --- | --- | --- | --- | --- | --- |
| R008 | authoring-pack.metadata-contract | P1 | F008 | ZIP review passed required metadata filenames without required provenance/source fields. | `zip_contract.py` now requires `provenance.json` and `source-manifest.json` contract fields before pass. |
| R009 | draft-validation.review-gate | P1 | F009 | `selected-skeleton-fill` could pass without review evidence. | CLI/request/application path now require `--review-report` and pass review gate fields into the result. |
| R010 | draft-validation.pack-digest-binding | P1 | F010 | issue draft adoption did not bind payload `draft_pack_digest` to review report pack digest by default. | application path now derives the expected draft pack digest from the pass review report when no explicit expected value is supplied. |
| R011 | authoring-pack.authority-scan | P1 | F011 | candidate JSON with documented `authorized_profile: null` was rejected by raw substring scanning. | ZIP review now sanitizes candidate JSON structurally for null `authorized_profile` before authority scanning. |

Local quality gates after this addendum:

- `make lint`: pass
- `uv run pytest tests/cli_runtime/test_authoring.py`: pass (`344 passed, 1 skipped`)
- `./spec-dock/scripts/spec-dock validate`: pass (`nodes=203`)

## Terminal Non-Blocking Report Boundary

When final re-observation contains only `P2`/`P3` findings:

- Do not update this batch solely to record them.
- Do not push a record-only commit.
- Do not trigger another review.
- Report those findings in the final response grouped by `root_cause_family`.
- State `branch mutation: no`.
- State `ci rerun avoided: yes`.
- State `review-clean: no`.
- State `merge-prepared: yes` if all blocking predicates are satisfied.

## Stop Conditions

Stop at a human gate when any condition applies:

- Any blocking inventory item remains `untriaged`.
- Any unresolved blocking `needs-human` item remains.
- A `P0`/`P1` `fix-now` repair unit is incomplete or repeatedly fails.
- The same `root_cause_family` reappears after a repair commit.
- Observation output is not for the latest head SHA.
- Timeout or observation limitation lacks resume metadata.
- Resume would cross the recorded trigger boundary.
- A new trigger would be required but has not been approved.
- Scope expansion, requirement expansion, breaking change, migration, secret,
  deployment setting, permission/auth, external/flaky, or ambiguous review
  intent is involved.
- Loop limits for the same root-cause family or total repair attempts are
  reached.
- GitHub branch protection requires conversation resolution for unresolved
  `P2`/`P3` threads; this is a platform human gate, not a code repair target.

## Merge-Prepared Gate

Report `merge-prepared: yes` only when all conditions are true:

- PR is open.
- Latest observation is complete and matches the latest head SHA.
- No observed required GitHub Actions CI failure remains.
- External/non-Actions check state has either been confirmed outside PR
  observation or is recorded as a human gate/residual risk.
- No unresolved `P0`/`P1` review feedback remains.
- Remaining `P2`/`P3` findings, if any, are grouped and reported as
  non-blocking terminal findings or recorded here because a blocking repair
  commit was already required.
- No visible merge conflict or equivalent semantic merge blocker remains.
- No blocking `untriaged` inventory item remains.
- No unresolved blocking `needs-human` item remains.
- No blocking item has an incomplete `fix-now` repair unit.
- Every repo-persistent `follow-up`, `no-action`, `covered-by`, `duplicate`, or
  `false-positive` item has rationale and residual risk where relevant.
- Observation limitation handling, resume metadata, trigger boundary, and new
  trigger approval status are recorded.
- Review-thread unresolved state is known, or unresolved-thread limitations are
  disclosed. If platform conversation resolution is required, stop at a human
  gate instead of claiming GitHub mergeability.
- `review-clean` is reported separately from `merge-prepared`.
- `github-mergeable` is not claimed unless platform requirements were confirmed.
