---
種別: pr-repair-batch
ID: "20260710t122133z-pr-repair-batch"
タイトル: "PR 311 Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-10"
親: ["iss-00309"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260710t122133z-pr-repair-batch PR 311 Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/311
- PR number: 311
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign
- Latest head SHA: 8c66118743ab55b3032d95eccd6eebf999fb06c2
- Observation command: `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 311 --head-sha 8c66118743ab55b3032d95eccd6eebf999fb06c2`
- Observation final JSON / evidence: status=human_gate, CI failed=2, P1 review findings=4
- Observation status: human_gate
- Trigger comment id: 4934997047
- Trigger created_at: 2026-07-10T11:53:33Z
- Trigger boundary: reviewed head 8c66118743ab55b3032d95eccd6eebf999fb06c2
- Resume metadata: not applicable; repair produces a new head
- New trigger approved: no
- Observation limitation: GitHub Actions and Codex review only; external checks are not observed
- Batch status: validated; ready to commit

## Batch Purpose

Use this repo-persistent batch to triage and repair blocking PR observation
results. A blocking result is a `P0`/`P1` review finding, required GitHub Actions
CI failure, visible merge conflict, blocking observation limitation, or other
merge-prepared blocker.

This batch separates raw intake from severity decisions, groups related findings
by `root_cause_family`, creates repair units only for blocking families, records
non-blocking findings only when a blocking repair commit is already being made,
and preserves residual risk for the final merge-prepared decision.

`root_cause_family` is documentation and LLM judgment vocabulary for this
discussion artifact. It is not a required runtime JSON field, parser contract,
blocker fingerprint, or stalled-observation contract.

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
| latest_head_sha | 8c66118743ab55b3032d95eccd6eebf999fb06c2 |
| observation_status | human_gate |
| required_ci_status | failed |
| review_status | unresolved |
| p0_count | 0 |
| p1_count | 4 |
| p2_count |  |
| p3_count |  |
| required_ci_failure_count | 2 duplicate workflow runs, one shared failure |
| merge_blocker_count | 5 concerns |
| blocking_family_count | 3 |
| non_blocking_family_count | 0 |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | no |
| merge_prepared_candidate | no |

## Raw Intake Inventory

Add one row per observed review finding, required CI failure, merge blocker, or
observation limitation from the same observation batch. Keep raw reviewer
priority separate from the final severity decision.

| item_id | source_type | source_id | reported_priority | path | line | raw_summary | evidence_type | current_head_sha | family_id | intake_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | review | 3558754353 | P1 | zip_contract.py | 230 | Windows drive-qualified ZIP entry is accepted | code-path | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F001 | triaged |
| R002 | review | 3558754356 | P1 | candidate_contract.py | 774 | Windows drive/backslash draft path is accepted | code-path | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F001 | triaged |
| R003 | review | 3558754361 | P1 | pack_prepare.py | 376 | Broken output-dir symlink bypasses rejection | code-path | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F002 | triaged |
| R004 | review | 3558754366 | P1 | pack_prepare.py | 349 | Exact initiatives root bypasses canonical target rejection | repro | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F002 | triaged |
| R005 | ci | Provider CI / test_wrappers | CI | tests/cli_runtime/test_wrappers.py | 136 | Current skill no longer references workflow_clarification.md | failing-test | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F003 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | authoring-pack.windows-path-boundary | Windows形式パスの境界検証 | yes | reviewed/staged pack内の参照はportable relative pathに限定する | R001,R002 | P1 | P1 | yes | fix-now | U001 | unit-created |
| F002 | prompt-pack.output-boundary | prompt-pack出力先の境界検証 | yes | canonical領域とsymlink経由の出力を拒否する | R003,R004 | P1 | P1 | yes | fix-now | U002 | unit-created |
| F003 | planning-skill.current-contract | ChatGPT-first skillの回帰契約 | no | scaffold testは現行skillの必要参照だけを要求する | R005 | CI | required-ci | yes | fix-now | U003 | unit-created |

## Classification Values

- `reported_priority`: `P0` / `P1` / `P2` / `P3` / `CI` / `unknown`
- `decided_priority`: `P0` / `P1` / `P2` / `P3` / `required-ci` / `platform` / `unknown`
- `merge_blocking`: `yes` / `no` / `platform-only` / `unknown`
- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<actions_job_or_workflow_name>` / `review_feedback:<stable_topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `platform_conversation_resolution` / `timeout` / `unknown`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Family Analysis

Create one subsection per real family.

### F001 authoring-pack.windows-path-boundary

- Related inventory IDs: R001, R002
- Reported priorities: P1, P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: path traversal and writes/reads outside reviewed evidence
- Contract / invariant: ZIP entry names and candidate draft paths must be portable, relative, and contained.
- Root cause: POSIX parsing alone did not reject drive-qualified or backslash Windows path forms.
- Why this is one family: both paths cross an evidence boundary through the same missing portable-path invariant.
- Validity analysis: valid and deterministic.
- Need-to-fix decision: yes.
- Options considered: platform-specific resolution; lexical portable-path rejection.
- Recommended disposition: lexical rejection before any Path join.
- Repair scope: ZIP relative-path validator, candidate draft validator, regression tests.
- Out of scope: host-specific Oracle paths.
- Quality gates: focused authoring tests and full provider suite.
- Residual risk: other path consumers remain covered by their existing validators.
- Follow-up handling: none.

### F002 prompt-pack.output-boundary

- Related inventory IDs: R003, R004
- Reported priorities: P1, P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: generated-file writes and symlink safety.
- Contract / invariant: prompt packs cannot write into canonical SpecDock data or through symlinked output paths.
- Root cause: existence-gated symlink checks miss broken links; canonical detection missed the exact initiatives root.
- Why this is one family: both defects bypass output-target rejection before file generation.
- Validity analysis: valid and deterministic.
- Need-to-fix decision: yes.
- Options considered: resolve-and-containment checks; minimal lexical root detection plus symlink checks independent of existence.
- Recommended disposition: preserve current structure and close both guard gaps.
- Repair scope: output target helpers and regression tests.
- Out of scope: redesign of all canonical path classification.
- Quality gates: focused authoring tests and full provider suite.
- Residual risk: string-based canonical matching remains conservative by design.
- Follow-up handling: none.

### F003 planning-skill.current-contract

- Related inventory IDs: R005
- Reported priorities: CI
- Decided priority: required-ci
- Merge-blocking: yes
- Protected domain: no.
- Contract / invariant: tests must assert the current minimal ChatGPT-first skill contract.
- Root cause: one wrapper test retained the retired clarification-document reference.
- Why this is one family: single stale assertion.
- Validity analysis: valid CI failure; product behavior is intentional.
- Need-to-fix decision: yes, update the test rather than reintroduce background guidance.
- Options considered: add the old reference back; remove stale assertion.
- Recommended disposition: remove stale assertion.
- Repair scope: tests/cli_runtime/test_wrappers.py only.
- Out of scope: skill body expansion.
- Quality gates: failed test and full provider suite.
- Residual risk: none.
- Follow-up handling: none.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260710t122133z-pr-repair-batch | F001 | R001,R002 | P1 | yes | fix-now | 20260710t122142z-disc-pr-repair-unit-windows-path-boundary.md | implemented | reject drive/backslash forms before joining | focused authoring tests | pending | pending | low |
| U002 | 20260710t122133z-pr-repair-batch | F002 | R003,R004 | P1 | yes | fix-now | 20260710t122142z-01-disc-pr-repair-unit-prompt-pack-output-boundary.md | implemented | close symlink and exact-root guard gaps | focused authoring tests | pending | pending | low |
| U003 | 20260710t122133z-pr-repair-batch | F003 | R005 | required-ci | yes | fix-now | 20260710t122142z-02-disc-pr-repair-unit-planning-skill-contract.md | implemented | remove stale test expectation | wrapper test and full provider suite | pending | pending | none |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |
| NBXXX | FXXX | RXXX | P2 / P3 |  |  |  |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G001 | F001 | targeted authoring path tests | unsafe Windows forms are rejected: pass | R001,R002 | yes |
| G002 | F002 | targeted prepare output tests | broken symlink and initiatives root are rejected: pass | R003,R004 | yes |
| G003 | F003 | test_scaffold_docs_point_to_runtime_commands_and_rules_docs | pass without retired reference | R005 | yes |
| G004 | all | uv run pytest | 2272 passed, 75 skipped | R001-R005 | yes |
| G005 | all | ./scripts/static_analysis/run.sh | ruff, format, mypy pass | R001-R005 | yes |
| G006 | all | ./spec-dock/scripts/spec-dock validate | ok, nodes=203 | R001-R005 | yes |

## Re-observation Plan

- Latest head before repair: 8c66118743ab55b3032d95eccd6eebf999fb06c2
- Expected head after repair:
- Re-observation command: wait_pr_observation.sh with the repaired head SHA
- Trigger mode: post-once
- Resume trigger comment id:
- Resume trigger created_at:
- New trigger approved: yes, required for the new pushed head
- Re-observation required because: all blocking findings and required CI must be checked on the repaired head
- Re-observation skipped because:

## Loop Control

| iteration | head_sha | observation_status | family_id | action_taken | fix_commit | reappeared_after_fix | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | human_gate | F001-F003 | repair implemented and validated | pending | no | commit, push, re-observe |

Stop at a human gate when the same `root_cause_family` reappears after a repair
commit, unless a human explicitly approves a new strategy.

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
