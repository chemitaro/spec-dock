---
name: github-pr-merge-preparer
description: Coordinate pull request creation or discovery, fixed Codex review triggering, PR observation, bounded fix delegation, re-push confirmation, and re-monitoring until a PR is merge-prepared for human judgment. Use when a workflow must continue after PR creation and report whether the PR is ready for a human merge decision without merging it.
---

# GitHub PR Merge Preparer

## Overview

Use this skill to coordinate the post-implementation PR delivery loop: create or find the PR, monitor the latest head SHA, create and triage a PR repair batch, delegate bounded fixes when appropriate, confirm commit and push evidence, re-monitor, and finally report either `merge-prepared` evidence or a human gate.

This skill is a workflow coordinator. It reuses `github-pr-creator` for PR creation, invokes `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` directly for fixed Codex review triggering plus checks/statuses/review observation, and delegates appropriate repair workers for implementation fixes. It does not implement CI log parsing, review repair logic, or GitHub write operations beyond the delegated branch push needed after an approved fix and the bounded `@codex review` trigger owned by `github-pr-observation`.

## Inputs

- Current repository, branch, and working tree state.
- Optional PR URL or number.
- Optional explicit base branch.
- Active issue context and issue-link expectations when available.
- Local final gate status so draft/ready intent can be chosen safely.

## Workflow

1. Confirm the current branch, working tree, remote repository, active issue context, and whether a PR already exists for the branch.
2. Resolve the base branch:
   - Reuse an existing PR when one exists, and do not create a duplicate.
   - If an existing PR exists, use its base for monitoring. If the user requested a conflicting base, stop at a human gate before mutating the PR.
   - If no PR exists, prefer an explicit user base.
   - Otherwise respect `branch.<current>.gh-merge-base` when present.
   - If docs, config, or branch hints conflict and no existing PR resolves the conflict, stop at a human gate before creating a PR.
   - Fall back to the repository default branch only when no stronger source exists.
3. Decide draft versus ready:
   - If local final gates are known to have passed, create or keep a ready PR unless the user explicitly requested draft.
   - If local final gates are incomplete or unknown, create a draft PR or stop at a human gate; do not present it as merge-prepared.
4. Create or find the PR through `github-pr-creator`, requiring PR URL, number, open/closed state, base branch, head branch, issue linkage, and latest head SHA in the return.
5. Invoke `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` directly with the repository, PR number, and latest head SHA. For a normal first observation, rely on the default `post-once` mode to post the fixed `@codex review` trigger. When continuing after a timeout or external limit, invoke explicit `--trigger-mode resume` with the trigger comment id / created_at from the previous final JSON. Treat the stdout final JSON as the primary result.
6. Treat observation output as stale when it is not for the latest head SHA. After every push or re-push, obtain the new latest head SHA and re-run `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`.
7. Before fix delegation, pass through the PR Repair Triage Gate:
   - Create or update a PR repair batch `disc` from the skill-local template `templates/pr-repair-batch.md` (`pr-repair-batch.md`). The template is the operational control sheet; prose-only notes in this skill are insufficient.
   - Add every review finding, CI failure, merge blocker, and observation limitation from the observation result to the batch `Inventory`.
   - Preserve PR metadata, latest head SHA, observation command, stdout final JSON location when available, trigger comment id / created_at, resume metadata, trigger boundary, and any observation limitation.
   - Do not post an unapproved new trigger while resuming a timeout or limit. Continue within the same trigger boundary with explicit resume metadata unless the user approves a new trigger.
   - Triage every inventory item before repair delegation; no item may remain `untriaged`.
   - Use the batch sections `Concern Catalog`, `Inventory`, `Per-Concern Analysis`, `Repair Queue`, `Unit Discussion Plan`, `Stop Conditions`, and `Merge-Prepared Gate`.
8. Classify failures with coarse labels only:
   - `check_failure:<job_or_check_name>`
   - `review_feedback:<topic>`
   - `merge_conflict`
   - `base_branch_conflict`
   - `permission_or_auth`
   - `external_or_flaky`
   - `timeout`
   - `unknown`
9. Apply the batch classification vocabulary to every inventory item:
   - `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
   - `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
   - `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
   - `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
   - `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`
10. Group related items by concern and same root cause. Multiple review findings and CI failures may share one repair unit when the batch rationale shows the common cause; duplicate or covered-by items must point to the covering item or repair unit.
11. For `follow-up`, `no-action`, `covered-by`, `duplicate`, or `false-positive` outcomes, record rationale, evidence, follow-up target when relevant, and residual risk in the batch. Do not silently dismiss an item.
12. For any `fix-now` item, and for any `needs-human` item that requires implementation analysis, design judgment, or comparison of options, create a repair unit `disc` before worker delegation. The repair unit must include `source_batch`, `unit_id`, `covered_ids`, `source_links`, `failure_class`, `risk_class`, `disposition`, `Validity Analysis`, `Need-To-Fix Decision`, `Root Cause`, `Options Considered`, `Recommended Design`, `Implementation Plan`, `Validation Plan`, `Implementation Result`, `Commit Evidence`, `Re-observation Result`, and `Residual Risk / Follow-up`.
13. Delegate bounded fixes only from repair unit `disc` artifacts, never from raw findings. The repair worker must use the repair unit discussion as the source of truth and follow its `Implementation Plan`; raw observation findings are supporting evidence only.
14. Confirm the delegated fix produced a commit and push for the PR head branch, update the batch repair unit status, then re-monitor the latest head SHA.
15. Stop with `merge-prepared` evidence when the predicate below is satisfied; otherwise stop at a human gate with the blocker history, batch state, and recommended next action.

## Fix Loop Limits

- Default autonomous repair limit is two repair attempts for the same `failure_class`.
- Default total autonomous repair limit is four repair attempts per PR preparation invocation.
- Stop at a human gate when the same `failure_class` appears after a repair, either limit is reached, or the blocker is `permission_or_auth`, `external_or_flaky`, `base_branch_conflict`, `unknown`, a requirement expansion, a breaking change, a migration, a secret or deployment setting change, or ambiguous review intent.
- Stop at a human gate when the PR repair batch has unresolved `needs-human` items, unresolved observation limitation, missing resume metadata for a timeout / limit continuation, a stale trigger boundary, or would require an unapproved new trigger.
- Record each loop as `iteration_index`, `head_sha`, `monitor_status`, `failure_class`, `action_taken`, and `next_action`.

## Merge-Prepared Predicate

`review-clean` and `merge-prepared` are different states. `review-clean` means the review has no actionable findings. `merge-prepared` means the latest head has been observed and all findings, failures, blockers, and residual risks are triaged so a human can make the merge decision. `review-clean: no` may still be `merge-prepared: yes` when remaining items are non-blocking and fully dispositioned.

Report `merge-prepared: yes` only when all of these are evidenced:

- PR is open.
- Monitor result is for the latest head SHA.
- Latest head re-observation has completed after the last repair commit or push.
- No required check failure remains.
- No non-required check failure remains unless the check is known optional or the user explicitly waived it.
- Any waived non-required check failure is reported as residual risk.
- No blocking review feedback remains.
- No visible merge conflict or equivalent merge blocker remains.
- PR repair batch exists from `templates/pr-repair-batch.md` / `pr-repair-batch.md`.
- No `untriaged` inventory item remains.
- No unresolved `needs-human` item remains.
- No `blocking` item with incomplete `fix-now` repair unit remains.
- Every `follow-up`, `no-action`, `covered-by`, `duplicate`, or `false-positive` item has rationale and residual risk where relevant.
- Timeout or observation limitation handling is explicit, with resume metadata and trigger boundary recorded.
- No unapproved new trigger was posted during resume or re-observation handling.
- Review-thread unresolved state is known, or an unresolved-thread limitation is explicitly disclosed and waived by the user.

If unresolved review-thread state cannot be determined and is not explicitly waived, stop at a human gate. Do not hide the limitation.

## Forbidden Writes

This skill must not perform or authorize:

- PR merge.
- Auto-merge enablement.
- Branch deletion.
- GitHub issue close.
- Running `spec-dock issue finish` or otherwise closing the active issue lifecycle.
- Review comment reply.
- Review thread resolve.
- Review dismiss.
- Admin override.
- Direct modification of PR observation script state or behavior.

## Human Gate Output

When stopping for a human gate, report:

- PR URL and number.
- Open/closed state.
- Base branch and head branch.
- Latest head SHA.
- Draft or ready state and why.
- Base-resolution source and any conflict.
- Monitor status and whether it matches the latest head SHA.
- PR repair batch path, untriaged count, unresolved `needs-human` count, and repair unit status.
- Resume metadata, trigger boundary, new trigger approval status, and observation limitation handling when relevant.
- Failure class history and attempted fixes.
- Non-required check waiver status, if relevant.
- Review-thread limitation status, if relevant.
- Remaining blocker and recommended next action.

## Response Checklist

- State whether a new PR was created or an existing PR was reused.
- State the selected base branch and why.
- State draft versus ready handling.
- Include PR URL, PR number, head branch, and latest head SHA.
- Summarize monitor results and fix-loop count.
- Include PR repair batch path, classification summary, repair queue, and whether repair workers used repair unit discussions instead of raw findings.
- Include `Implementation Plan`, `Re-observation Result`, and `Residual Risk` status for each repair unit that affected the final decision.
- State `review-clean: yes/no` separately from `merge-prepared: yes/no`.
- State whether the PR is `merge-prepared: yes` or `merge-prepared: no`.
- If `merge-prepared: yes`, include the evidence predicate and residual risks.
- If `merge-prepared: no`, include the human gate reason and next action.
- State explicitly that merge remains a human action.
