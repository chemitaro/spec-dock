---
name: github-pr-merge-preparer
description: Coordinate pull request creation or discovery, fixed Codex review triggering, PR observation, severity-aware batch triage, bounded P0/P1 repair delegation, re-push confirmation, and re-monitoring until a PR is merge-prepared for human judgment. Use when a workflow must continue after PR creation and report whether the PR is ready for a human merge decision without merging it.
---

# GitHub PR Merge Preparer

## Overview

Use this skill to coordinate the post-implementation PR delivery loop: create or
find the PR, monitor the latest head SHA, observe GitHub Actions CI and Codex PR
review feedback, triage the observation as one batch, delegate bounded repairs
only for blocking findings, confirm commit/push evidence, re-monitor when the
branch changes, and finally report either `merge-prepared` evidence or a human
gate.

This skill is a workflow coordinator. It reuses `github-pr-creator` for PR
creation, invokes
`./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
directly for fixed Codex review triggering plus GitHub Actions CI and review
observation, and delegates appropriate repair workers for implementation fixes.
It does not implement CI log parsing, review repair logic, GitHub issue closing,
review thread resolution, review dismissal, or PR merging.

## Inputs

- Current repository, branch, and working tree state.
- Optional PR URL or number.
- Optional explicit base branch.
- Active issue context and issue-link expectations when available.
- Local final gate status so draft/ready intent can be chosen safely.
- Optional existing PR repair batch path when continuing blocking repair work.

## Core concepts

### Review severity

- `P0`: critical blocker. Blocks merge.
- `P1`: merge-blocking defect. Blocks merge.
- `P2`: material non-blocking follow-up. Does not block merge.
- `P3`: minor advisory. Does not block merge.

Only `P0` and `P1` review findings are autonomous repair scope. Required
GitHub Actions CI failures and visible merge conflicts are also blocking repair
or human-gate inputs.

`P2` and `P3` findings are not ignored. They are triaged as non-blocking review
information, but this skill must not mutate the PR branch, create repair units,
push, or trigger another review solely to persist or address `P2`/`P3`
findings.

### Review-clean vs merge-prepared

`review-clean` and `merge-prepared` are different states.

- `review-clean: yes` means no observed `P0`/`P1`/`P2`/`P3` review findings
  remain.
- `merge-prepared: yes` means the latest head has been observed, required CI
  and blocking review findings are clear, and any remaining non-blocking
  findings are explicitly reported for human judgment.

A PR can be `merge-prepared: yes` while `review-clean: no` when only `P2`/`P3`
findings remain.

### Root-cause family

Do not process review comments one-by-one. Treat each observation as a batch and
group related findings into stable `root_cause_family` values. Multiple review
comments and CI failures may share one repair unit when the batch rationale
shows the same underlying contract, detector, parser, state-machine invariant,
mirror-sync rule, or generated-artifact rule.

Examples:

- `issue_readiness.placeholder_contract`
- `pr_observation.blocker_policy`
- `provider_asset.dogfooding_parity`
- `assurance_contract.serialization`
- `workflow_report_gate.value_normalization`

The reviewer-suggested `root_cause_family` is advisory. The merge preparer makes
the final grouping decision. Treat `root_cause_family` as documentation and LLM
judgment vocabulary, not as a required observation runtime JSON field, parser
contract, blocker fingerprint, or stalled-observation contract.

## Workflow

1. Confirm the current branch, working tree, remote repository, active issue
   context, and whether a PR already exists for the branch.
2. Resolve the base branch:
   - Reuse an existing PR when one exists, and do not create a duplicate.
   - If an existing PR exists, use its base for monitoring.
   - If the user requested a conflicting base, stop at a human gate before
     mutating the PR.
   - If no PR exists, prefer an explicit user base.
   - Otherwise respect `branch.<current>.gh-merge-base` when present.
   - If docs, config, or branch hints conflict and no existing PR resolves the
     conflict, stop at a human gate before creating a PR.
   - Fall back to the repository default branch only when no stronger source
     exists.
3. Decide draft versus ready:
   - If local final gates are known to have passed, create or keep a ready PR
     unless the user explicitly requested draft.
   - If local final gates are incomplete or unknown, create a draft PR or stop
     at a human gate; do not present it as merge-prepared.
4. Create or find the PR through `github-pr-creator`, requiring PR URL, number,
   open/closed state, base branch, head branch, issue linkage, and latest head
   SHA in the return.
5. Invoke `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
   directly with the repository, PR number, and latest head SHA. For a normal
   first observation, rely on default `post-once` mode to post the fixed
   `@codex review` trigger. When continuing after a timeout or external limit,
   invoke explicit `--trigger-mode resume` with the trigger comment id /
   created_at from the previous final JSON. Treat the stdout final JSON as the
   primary result.
6. Treat observation output as stale when it is not for the latest head SHA.
   After every push or re-push, obtain the new latest head SHA and re-run
   `wait_pr_observation.sh`.
7. Classify the latest observation as one of:
   - `blocking_repair_required`
   - `blocking_human_gate`
   - `terminal_non_blocking_only`
   - `merge_prepared_clean`
   - `wait_or_resume`
   - `unknown_human_gate`
8. If blocking repair is required, create or update a repo-persistent PR repair
   batch and perform family-based repair as described below.
9. If the latest observation contains only `P2`/`P3` findings and no required CI
   failure, no merge conflict, no blocking observation limitation, and no `P0`/
   `P1` review blocker, do not mutate the branch. Report a terminal
   non-blocking finding summary in the final response and mark
   `merge-prepared: yes` when the remaining merge-prepared predicate is met.
10. Stop with `merge-prepared` evidence when the predicate below is satisfied;
    otherwise stop at a human gate with blocker history, batch state, and
    recommended next action.

## PR Repair Batch Gate

A repo-persistent PR repair batch is required only when blocking repair or
blocking triage is performed.

Create or update a PR repair batch when any of the following exists:

- `P0` or `P1` review finding.
- Required GitHub Actions CI failure.
- Visible merge conflict or equivalent merge blocker.
- Blocking observation limitation requiring repair or human-gate tracking.
- Blocking platform condition that must be documented with branch mutation that
  is already required for repair.

Do not create or update a repo-persistent PR repair batch solely to record
terminal `P2`/`P3` findings after the latest pushed head has no blockers.

When a writable SpecDock issue scope exists and a batch is required, run:

```bash
./spec-dock/scripts/spec-dock new artifact pr-repair-batch --issue <issue-id> --title "PR Repair Batch"
```

Use the appropriate scope flag, capture `path=...`, and edit only that generated
path. The generated file owns all front matter identity fields. Use
`templates/pr-repair-batch.md` from this skill directory only as body-section scaffold below
the generated heading/front matter. When continuing an existing batch path,
preserve its front matter identity fields and update only the batch body.

When no writable SpecDock issue scope exists, maintain an inline PR repair batch
section in the response or work log using the same body sections and state
`batch_path: N/A`.

## Batch triage policy

For a blocking repair batch:

1. Add every observed review finding, required Actions CI failure, merge blocker,
   and observation limitation from the observation result to the batch Raw Intake
   Inventory.
2. Keep the reported reviewer priority in `reported_priority`; do not silently
   promote `P2`/`P3` to `P1`.
3. Group items by `root_cause_family` before selecting repair units.
4. Determine `decided_priority` per family:
   - `P0` / `P1`: blocking repair or human gate.
   - `P2` / `P3`: non-blocking no-action or follow-up.
5. Create repair units only for `P0`/`P1` families and required CI failures.
6. Record `P2`/`P3` families in the Non-Blocking Follow-up Register when a
   blocking repair commit is already being prepared.
7. Do not expand repair scope to fix `P2`/`P3` unless the fix is directly and
   unavoidably covered by the same `P0`/`P1` root-cause repair. In that case,
   record the coverage rationale.
8. Triage every inventory item before repair delegation; no item may remain
   `untriaged` in a repo-persistent blocking repair batch.

## Classification vocabulary

Use these coarse failure classes:

- `check_failure:<actions_job_or_workflow_name>`
- `review_feedback:<stable_topic>`
- `merge_conflict`
- `base_branch_conflict`
- `permission_or_auth`
- `external_or_flaky`
- `platform_conversation_resolution`
- `timeout`
- `unknown`

Use these inventory fields:

- `reported_priority`: `P0` / `P1` / `P2` / `P3` / `CI` / `unknown`
- `decided_priority`: `P0` / `P1` / `P2` / `P3` / `required-ci` /
  `platform` / `unknown`
- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` /
  `unknown`
- `merge_blocking`: `yes` / `no` / `platform-only` / `unknown`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` /
  `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` /
  `implemented` / `reobserved-pass` / `blocked`

## Repair unit policy

For every `P0`/`P1` family and required CI failure that is repairable within
scope, create a repair unit before worker delegation.

Repair units remain ordinary `disc` artifacts; do not require or invent a
`pr-repair-unit` doc type. When a writable SpecDock issue scope exists, run:

```bash
./spec-dock/scripts/spec-dock new artifact disc --issue <issue-id> --title "PR Repair Unit <unit_id>" --slug "pr-repair-unit-<unit-slug>"
```

Use the appropriate scope flag, capture `path=...`, and edit only that generated
path. Derive `unit-slug` as a lowercase kebab-case filename component separate
from display `unit_id`.

A repair unit must include:

- `source_batch`
- `unit_id`
- `root_cause_family`
- `covered_ids`
- `source_links`
- `failure_class`
- `decided_priority`
- `merge_blocking`
- `disposition`
- `Validity Analysis`
- `Need-To-Fix Decision`
- `Root Cause`
- `Options Considered`
- `Recommended Design`
- `Implementation Plan`
- `Validation Plan`
- `Out of Scope`
- `Implementation Result`
- `Commit Evidence`
- `Re-observation Result`
- `Residual Risk / Follow-up`

Delegate bounded fixes only from repair unit artifacts or inline repair units,
never from raw findings. The repair worker must use the repair unit as the
source of truth and follow its `Implementation Plan`; raw observation findings
are supporting evidence only.

## Terminal non-blocking observation policy

When the latest observation contains only `P2`/`P3` review findings and no
required CI failure, no merge conflict, no blocking observation limitation, and
no `P0`/`P1` review blocker:

- Do not mutate the PR branch solely to record those findings.
- Do not create or update a repo-persistent PR repair batch solely for those
  findings.
- Do not delegate repair workers.
- Do not push.
- Do not trigger another review.
- Report `review-clean: no`.
- Report `merge-prepared: yes` when the remaining merge-prepared predicate is
  satisfied.
- Include a terminal non-blocking report grouped by `root_cause_family`.
- State `branch mutation: no` and `ci rerun avoided: yes`.

If a previous blocking repair batch exists, do not update it solely to add
terminal `P2`/`P3` findings after the final clean blocking re-observation. Record
those findings in the final response instead and disclose that the batch was not
updated to avoid a record-only push.

## Platform conversation-resolution policy

Semantic severity and GitHub platform mergeability are separate.

If branch protection requires unresolved conversations to be resolved, a `P2`/
`P3` inline review thread may become a platform blocker even though it is not a
semantic code blocker. This skill must not resolve review threads, dismiss
reviews, or post review replies.

In that case, stop at a human gate:

- `human_gate_reason: platform_conversation_resolution_required`
- `recommended_next_action: human_resolve_or_acknowledge_non_blocking_threads`

Do not perform code repair solely to satisfy platform conversation resolution
for `P2`/`P3` findings.

## Fix loop limits

- Default autonomous repair limit is one repair attempt for `P0` family unless
  the fix is trivial and fully local.
- Default autonomous repair limit is two repair attempts for the same `P1`
  `root_cause_family`.
- Default total autonomous repair limit is four repair attempts per PR
  preparation invocation.
- Stop at a human gate when the same `root_cause_family` appears after a repair
  commit.
- Stop at a human gate when the blocker is `permission_or_auth`,
  `external_or_flaky`, `base_branch_conflict`, `unknown`, a requirement
  expansion, breaking change, migration, secret/deployment setting change,
  ambiguous review intent, or platform-only conversation resolution.
- Stop at a human gate when a repair would require a new unapproved review
  trigger, stale trigger boundary, unresolved observation limitation, or missing
  resume metadata for timeout/limit continuation.
- Record each loop as `iteration_index`, `head_sha`, `observation_status`,
  `root_cause_family`, `action_taken`, `fix_commit`, and `next_action`.

## Merge-prepared predicate

Report `merge-prepared: yes` only when all of these are evidenced:

- PR is open.
- Monitor result is for the latest head SHA.
- Latest head re-observation has completed after the last repair commit or push,
  unless no branch mutation was performed for a terminal `P2`/`P3`-only
  observation.
- No observed required GitHub Actions CI failure remains.
- External/non-Actions checks are not claimed as observed by this skill. If
  branch protection or repository workflow depends on them, GitHub UI or
  external CI confirmation is recorded, or the PR stops at a human gate.
- Any waived or unconfirmed external/non-Actions check risk is reported as
  residual risk.
- No unresolved `P0`/`P1` review feedback remains.
- Remaining `P2`/`P3` feedback, if any, is grouped and reported as
  non-blocking terminal findings or recorded in the blocking repair batch when
  a repair commit was already required.
- No visible merge conflict or equivalent semantic merge blocker remains.
- If blocking repair was performed, a PR repair batch exists at the
  runtime-generated `new artifact pr-repair-batch` path when a writable SpecDock
  scope exists, or as an inline batch with `batch_path: N/A` when no writable
  scope exists.
- No `untriaged` blocking inventory item remains in any repo-persistent repair
  batch.
- No unresolved `needs-human` blocking item remains.
- No `blocking` item has an incomplete `fix-now` repair unit.
- Every repo-persistent `follow-up`, `no-action`, `covered-by`, `duplicate`, or
  `false-positive` item has rationale and residual risk where relevant.
- Timeout or observation limitation handling is explicit, with resume metadata
  and trigger boundary recorded.
- No unapproved new trigger was posted during resume or re-observation handling.
- Review-thread unresolved state is known, or unresolved-thread limitations are
  explicitly disclosed. If branch protection requires conversation resolution
  and unresolved `P2`/`P3` threads remain, stop at the platform human gate
  instead of claiming GitHub mergeability.

Do not claim `github-mergeable: yes` unless GitHub platform requirements
including branch protection, required checks, required reviews, and conversation
resolution have been confirmed. This skill may report `merge-prepared: yes`
without claiming `github-mergeable: yes`.

## Forbidden writes

This skill must not perform or authorize:

- PR merge.
- Auto-merge enablement.
- Branch deletion.
- GitHub issue close.
- Running `spec-dock issue finish` or otherwise closing the active issue
  lifecycle.
- Review comment reply.
- Review thread resolve.
- Review dismiss.
- Admin override.
- Direct modification of PR observation script state or behavior.

## Human gate output

When stopping for a human gate, report:

- PR URL and number.
- Open/closed state.
- Base branch and head branch.
- Latest head SHA.
- Draft or ready state and why.
- Base-resolution source and any conflict.
- Monitor status and whether it matches the latest head SHA.
- PR repair batch path when one exists or `N/A` when no blocking repair batch
  was required.
- Blocking untriaged count, unresolved `needs-human` count, and repair unit
  status.
- Terminal `P2`/`P3` findings if present and why no branch mutation was made.
- Resume metadata, trigger boundary, new trigger approval status, and
  observation limitation handling when relevant.
- Failure family history and attempted fixes.
- External/non-Actions check confirmation or waiver status, if relevant.
- Platform conversation-resolution status, if relevant.
- Remaining blocker and recommended next action.

## Response checklist

- State whether a new PR was created or an existing PR was reused.
- State the selected base branch and why.
- State draft versus ready handling.
- Include PR URL, PR number, head branch, and latest head SHA.
- Summarize monitor results and fix-loop count.
- State whether a repo-persistent repair batch was required.
- Include repair batch path when one exists.
- Include classification summary grouped by `root_cause_family`.
- State whether repair workers used repair unit artifacts instead of raw
  findings.
- Include `Implementation Plan`, `Re-observation Result`, and `Residual Risk`
  status for each repair unit that affected the final decision.
- For terminal `P2`/`P3`-only observations, include `branch mutation: no`,
  `ci rerun avoided: yes`, and the grouped non-blocking findings.
- State `review-clean: yes/no` separately from `merge-prepared: yes/no`.
- State whether the PR is `merge-prepared: yes` or `merge-prepared: no`.
- Do not claim `github-mergeable: yes` unless platform requirements were
  checked.
- If `merge-prepared: yes`, include the evidence predicate and residual risks.
- If `merge-prepared: no`, include the human gate reason and next action.
- State explicitly that merge remains a human action.
