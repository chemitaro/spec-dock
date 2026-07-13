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
- Latest head SHA: 53a965d32d337df78de8eefdfacca372ae089c8c
- Observation command: `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 321 --head-sha a2bb97369031b24c892d21836559a238c938ce52`
- Observation status: timeout; CI running; current review contains one P1 and three P2; four carryover P2 remain unresolved
- Trigger comment id: 4955352817
- Trigger created_at: 2026-07-13T07:10:00Z
- Trigger boundary: current head 53a965d32d337df78de8eefdfacca372ae089c8c
- Resume metadata: available for same head, but branch mutation is required by P1
- New trigger approved: default post-once for new head only
- Observation limitation: none
- Batch status: second_blocking_repair_validated_pending_push

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
| R003 | review | comment 3568746650 | P1 | query parameters such as access_token/oauth_token are not redacted | deterministic-probe | 53a965d32d337df78de8eefdfacca372ae089c8c | F002 | triaged |
| R004 | review | comment 3568746654 | P2 | default source manifest omits new infra modules | contract-follow-up | 53a965d32d337df78de8eefdfacca372ae089c8c | F003 | triaged |
| R005 | review | comment 3568746660 | P2 | multi-method SSH denial is classified as local permission failure | deterministic-probe | 53a965d32d337df78de8eefdfacca372ae089c8c | F004 | triaged |
| R006 | review | comment 3568746665 | P2 | Windows drive/UNC origins can expose local paths | edge-case-review | 53a965d32d337df78de8eefdfacca372ae089c8c | F005 | triaged |
| R007 | carryover review | comment 3568618494 | P2 | default source manifest omits infra modules | contract-follow-up | 53a965d32d337df78de8eefdfacca372ae089c8c | F003 | duplicate |
| R008 | carryover review | comment 3568618499 | P2 | pass receipt validation does not require attempt evidence | malformed-input-follow-up | 53a965d32d337df78de8eefdfacca372ae089c8c | F006 | triaged |
| R009 | carryover review | comment 3568618503 | P2 | curl-style `returned error: 503` is not transient | edge-case-review | 53a965d32d337df78de8eefdfacca372ae089c8c | F007 | triaged |
| R010 | carryover review | comment 3568618507 | P2 | relative local origin resolution depends on process cwd | provenance-follow-up | 53a965d32d337df78de8eefdfacca372ae089c8c | F008 | triaged |

## Concern Family Catalog

| family_id | root_cause_family | family_title | invariant_or_contract | related_items | decided_priority | merge_blocking | disposition | repair_unit | family_status |
|---|---|---|---|---|---|---|---|---|---|
| F001 | static-analysis.format-contract | Changed Python files are not canonical Ruff format | Provider CI required static-analysis gate | R001,R002 | required-ci | yes | fix-now | U001 | unit-created |
| F002 | fetch-diagnostic-redaction | Credential query parameter redaction | durable diagnostic secrecy | R003 | P1 | yes | fix-now | U002 | unit-created |
| F003 | source-manifest-coverage | Default manifest excludes infra | default provenance completeness | R004,R007 | P2 | no | follow-up | N/A | triaged |
| F004 | fetch-classification-auth-denial | Multi-method SSH denial classification | remediation accuracy | R005 | P2 | no | follow-up | N/A | triaged |
| F005 | normalized-origin-local-path-privacy | Windows local origin privacy | cross-platform path privacy | R006 | P2 | no | follow-up | N/A | triaged |
| F006 | receipt-pass-semantic-validation | Attempt evidence validation | malformed receipt defense | R008 | P2 | no | follow-up | N/A | triaged |
| F007 | fetch-transient-classification | Curl-style 5xx classification | edge-case retry coverage | R009 | P2 | no | follow-up | N/A | triaged |
| F008 | relative-origin-normalization | Relative origin resolution | provenance determinism | R010 | P2 | no | follow-up | N/A | triaged |

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
| U002 | 20260713t064556z-pr-repair-batch | F002 | R003 | P1 | yes | fix-now | 20260713t074058z-disc-pr-repair-unit-diagnostic-token-redaction.md | implemented | redact credential-like query keys before excerpt/digest | focused security/lint/mypy/parity pass | `4429681577c46d891ac59fb6ad7e0968352077f6` | pending | low |

## Non-Blocking Follow-up Register

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
|---|---|---|---|---|---|---|
| NB001 | F003 | R004,R007 | P2 | explicitly non-blocking; not unavoidable within P1 redaction repair | default manifest can omit infra changes | follow-up Issue |
| NB002 | F004 | R005 | P2 | safe block remains; remediation classification only | operator may receive less accurate hint | follow-up Issue |
| NB003 | F005 | R006 | P2 | non-default Windows local origin edge | Windows receipt may expose local path | follow-up Issue |
| NB004 | F006 | R008 | P2 | malformed hand-edited receipt edge; current generated receipt is valid | weaker semantic validation | follow-up Issue |
| NB005 | F007 | R009 | P2 | unknown fails closed; bounded retry opportunity only | curl-style 5xx misses retry | follow-up Issue |
| NB006 | F008 | R010 | P2 | relative local origin edge; no safety false pass | provenance hash may depend on cwd | follow-up Issue |

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
| 2 | 53a965d32d337df78de8eefdfacca372ae089c8c | timeout / blocker_present | F002 | U002 implemented/fresh-reviewed; P2 families triaged follow-up | `4429681577c46d891ac59fb6ad7e0968352077f6` | no | commit evidence docs、push and re-observe |
