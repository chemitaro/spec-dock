---
種別: pr-repair-batch
ID: "20260713t064556z-pr-repair-batch"
タイトル: "PR Repair Batch"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00314"]
関連: ["PR #321"]
authority: "proposed"
derived_from: ["PR #321 observation at a2bb97369031b24c892d21836559a238c938ce52"]
reflected_to: ["report.md"]
---

# PR Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/321
- PR number: 321
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00314-harden-github-sync-preflight-fetch-and-receipt-contract
- Latest head SHA: a2bb97369031b24c892d21836559a238c938ce52
- Observation command: `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 321 --head-sha a2bb97369031b24c892d21836559a238c938ce52`
- Observation status: failed / fix_ci
- Trigger comment id: 4955181352
- Trigger created_at: 2026-07-13T06:45:42Z
- Trigger boundary: current head a2bb97369031b24c892d21836559a238c938ce52
- Resume metadata: not applicable after branch mutation
- New trigger approved: default post-once for new head only
- Observation limitation: none
- Batch status: repair_validated_pending_commit

## Observation Batch Summary

| field | value |
|---|---|
| latest_head_sha | a2bb97369031b24c892d21836559a238c938ce52 |
| observation_status | failed |
| required_ci_status | Provider CI failed; CI validate passed |
| review_status | no completion yet |
| p0/p1/p2/p3_count | 0 / 0 / 0 / 0 |
| required_ci_failure_count | 2 duplicate workflow runs, same root cause |
| blocking_family_count | 1 |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | unknown |
| merge_prepared_candidate | no |

## Raw Intake Inventory

| item_id | source_type | source_id | reported_priority | raw_summary | evidence_type | current_head_sha | family_id | intake_status |
|---|---|---|---|---|---|---|---|---|
| R001 | ci | Provider CI run 29229910006 / job 86751677920 | CI | `make lint` failed at `ruff format --check`; 7 files would be reformatted | failing-check-log | a2bb97369031b24c892d21836559a238c938ce52 | F001 | triaged |
| R002 | ci | Provider CI run 29229887985 / job 86751613656 | CI | duplicate run with the same `ruff format --check` failure | failing-check-log | a2bb97369031b24c892d21836559a238c938ce52 | F001 | triaged |

## Concern Family Catalog

| family_id | root_cause_family | family_title | invariant_or_contract | related_items | decided_priority | merge_blocking | disposition | repair_unit | family_status |
|---|---|---|---|---|---|---|---|---|---|
| F001 | static-analysis.format-contract | Changed Python files are not canonical Ruff format | Provider CI required static-analysis gate | R001,R002 | required-ci | yes | fix-now | U001 | unit-created |

## F001 static-analysis.format-contract

- Validity: valid; logs identify only `ruff format --check`.
- Root cause: implementation and test files pass Ruff lint but were not normalized by Ruff formatter.
- Why one family: both workflow failures are duplicate executions of the same head and same format invariant.
- Need to fix: yes; required Provider CI blocks merge.
- Options: format only reported files, or run formatter over the repository. Adopt the first to keep the repair bounded.
- Repair scope: the seven files reported by CI, plus provider/dogfood parity refresh only if formatting changes an authoritative provider mirror.
- Out of scope: semantic changes, refactors, P2/P3 work, workflow changes.
- Quality gates: `uv run ruff format --check src tests`, `uv run ruff check src tests`, focused tests, provider/dogfood parity, diff check.
- Residual risk: formatter may reveal mirror drift; parity must be rechecked.

## Blocking Repair Queue

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U001 | 20260713t064556z-pr-repair-batch | F001 | R001,R002 | required-ci | yes | fix-now | 20260713t064629z-disc-pr-repair-unit-static-format-gate.md | implemented | Ruff-format only CI-reported files and synchronize required mirrors | format/lint/mypy/focused 1013/parity pass | `411510b66abd3dcd137fbed598606065134457e5` | pending | low |

## Non-Blocking Follow-up Register

No P2/P3 findings were observed in this batch.

## Re-observation Plan

- Latest head before repair: a2bb97369031b24c892d21836559a238c938ce52
- Expected head after repair evidence commit: pending final docs commit; implementation commit `411510b66abd3dcd137fbed598606065134457e5`
- Trigger mode: post-once on the new head
- New trigger approved: yes, normal new-head observation
- Re-observation required because: required CI failure requires branch mutation.

## Loop Control

| iteration | head_sha | observation_status | family_id | action_taken | fix_commit | reappeared_after_fix | next_action |
|---|---|---|---|---|---|---|---|
| 1 | a2bb97369031b24c892d21836559a238c938ce52 | failed | F001 | U001 implemented and fresh-reviewed | `411510b66abd3dcd137fbed598606065134457e5` | no | commit evidence docs、push and re-observe |
