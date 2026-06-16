---
種別: disc
ID: "20260616t024310z-disc-pr-repair-batch"
タイトル: "PR repair batch for PR #189"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
親: ["iss-00186"]
関連: ["#189"]
authority: "proposed"
derived_from: [".agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md"]
reflected_to: []
---

# PR repair batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/189
- PR number: 189
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00186-harden-issue-execution-step-gates
- Latest head SHA: bfa488939e24bb2d399b6260a56b5ef69cdd68ca
- Observation command: `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 189 --head-sha e1b1fd25443eeeb283f9dff50f370323fc8c0fb7 --timeout-seconds 1800 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --out /private/tmp/iss-00186-pr-observation`
- Observation final JSON / evidence: `/private/tmp/iss-00186-pr-observation/result.json`
- Observation status: initial failed; post-repair re-observation CI passed with conservative `human_gate`
- Trigger comment id: 4710558399
- Trigger created_at: 2026-06-15T17:31:22Z
- Trigger boundary: current trigger boundary for head `e1b1fd25443eeeb283f9dff50f370323fc8c0fb7`
- Resume metadata: not applicable; observation reached terminal failed state
- New trigger approved: no
- Observation limitation: post-repair Codex review completion remained `fallback_issue_comment_low_confidence`; CI passed, body says no major issues, and unresolved thread state is known as zero
- Batch status: reobserved-pass for CI; conservative human gate for review signal confidence

## Batch Purpose

Use this batch to triage review findings, CI failures, merge blockers, and observation limitations after PR observation and before repair delegation.

## Concern Catalog

| concern_id | concern | related_inventory_ids | suspected_root_cause | repair_unit | notes |
| --- | --- | --- | --- | --- | --- |
| C001 | PR event `provider-tests` failed on dogfooding `.meta.json` snapshot drift | I001 | base `main` contains `iss-00187` while the branch snapshot assertions were authored before that base commit | U001 | push event provider-tests passed for the same head; PR merge-commit event failed because it included the newer base issue metadata |

## Inventory

| ID | source_type | concern | failure_class | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status | rationale | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I001 | CI failure | C001 | check_failure:provider-tests | PR observation result and `gh run view 27564309099 --log-failed` | `TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` failed because observed `.meta.json` paths include `iss-00187-actions-pr-observation-ci-state/.meta.json` in the PR merge commit | valid | blocking | yes | fix-now | U001 | reobserved-pass | Branch merge state includes `origin/main` and the snapshot path / `depends_on` baselines now include `iss-00187`; focused pytest, `spec-dock validate`, `code-reviewer` pass, and post-repair CI re-observation passed 4/4 checks. | Low; snapshot can drift again if `main` gains another dogfooding node before merge |

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
- Validity analysis: valid; latest PR observation has one failing `provider-tests` check for head `e1b1fd25443eeeb283f9dff50f370323fc8c0fb7`.
- Need-to-fix decision: yes.
- Root cause: `origin/main` advanced with `iss-00187-actions-pr-observation-ci-state`; PR event tests run against a merge commit including base changes, while the branch snapshot baseline does not include the new `.meta.json`.
- Options considered:
  - Rerun failed CI without branch changes: rejected because the PR event failure is deterministic snapshot drift.
  - Merge/rebase `origin/main` and update snapshot baselines: selected because it makes branch expectations match the merge base state.
  - Waive the non-required check: rejected because `provider-tests` is material provider CI.
- Recommended disposition: fix-now via U001.
- Rationale: merge-prepared predicate requires no check failure remains.
- Residual risk: the snapshot remains sensitive to concurrent dogfooding issue additions on `main`.

## Repair Queue

| unit_id | source_batch | covered_ids | disposition | risk_class | repair_unit_disc | status | Implementation Plan | Re-observation Result | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | `20260616t024310z-disc-pr-repair-batch.md` | I001 | fix-now | blocking | `20260616t024410z-disc-pr-repair-unit-u001-provider-tests-snapshot-drift.md` | reobserved-pass | Synced branch with `origin/main`, updated dogfooding snapshot baselines for `iss-00187`, ran focused provider test and SpecDock validate. | `/private/tmp/iss-00186-pr-observation-r2/result.json` and resume result: CI passed 4/4 on `bfa488939e24bb2d399b6260a56b5ef69cdd68ca`; review signal is fallback issue comment with no major issues and zero unresolved threads | Snapshot can drift again if `main` gains another dogfooding node before merge. |

## Unit Discussion Plan

Create a repair unit `disc` for U001. The worker must use the repair unit discussion, not raw findings, as the source of truth.

## Stop Conditions

- Any inventory item remains `untriaged`: no.
- Any unresolved `needs-human` item remains: no.
- A blocking `fix-now` repair unit is incomplete or repeatedly fails: no; U001 implemented and pending re-observation.
- Observation output is not for the latest head SHA: no.
- Timeout or observation limitation lacks resume metadata: no timeout.
- Scope expansion, requirement expansion, breaking change, migration, secret, deployment setting, permission/auth, external/flaky, or ambiguous review intent is involved: no.

## Merge-Prepared Gate

- PR is open: yes.
- Latest head re-observation is complete and matches the latest head SHA: CI re-observation matches latest head and passed; review observation remains conservative `human_gate` due fallback issue comment.
- No required check failure remains: yes, post-repair checks passed 4/4.
- No blocking review feedback remains: yes, no major Codex issues observed and no unresolved threads.
- No visible merge conflict or equivalent merge blocker remains: yes, PR metadata reported mergeable before repair.
- No `untriaged` inventory item remains: yes.
- No unresolved `needs-human` item remains: yes.
- No `blocking` item has an incomplete `fix-now` repair unit: yes, U001 reobserved-pass for CI.
- Review-thread unresolved state is known: yes, observation reported `threads.state_available=true` and `unresolved=0`.
- review-clean: yes for current observed review body, with fallback issue-comment confidence noted.
- merge-prepared: human gate by observation-script semantics because review completion did not promote beyond fallback issue comment; GitHub PR metadata is open / ready / mergeable and checks are green.
