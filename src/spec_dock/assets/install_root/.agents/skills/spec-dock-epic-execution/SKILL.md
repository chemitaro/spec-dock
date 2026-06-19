---
name: spec-dock-epic-execution
description: First-read coordinator for executing a planned spec-dock Epic through one Issue at a time, routing to existing Issue planning, Issue execution, PR preparation, and completion gates.
---

# Spec-Dock Epic Execution

Use this skill after Epic planning is complete and the Epic requirement, design, and plan are ready for downstream Issue work. This skill is a coordinator only; keep detailed lifecycle rules in `spec-dock/docs/workflow_epic.md`, `spec-dock/docs/workflow_issue.md`, and the existing leaf skills.

## First-Read Coordinator Flow

1. Bootstrap current state.
   - Resolve an explicitly requested Epic to the active Epic, or route the required lifecycle activation / selection step before applying active-Epic checks.
   - Confirm the active Epic and read its reviewed planning outputs.
   - Check `./spec-dock/scripts/spec-dock active show` for an active Issue.
   - Check git/projection/GitHub freshness as needed for the user's request, using `sync`, `sync --github`, `validate`, `git status`, `git fetch`, or GitHub inspection when stale state could affect Issue readiness or PR delivery.
   - If no active Epic remains after requested-Epic resolution, or no reviewed Epic planning handoff exists, stop and route back to `spec-dock-epic-planning` or the Epic workflow.
2. If an active Issue already exists, stop before selecting another Issue.
   - Require a continuation, finish evaluation, or explicit user decision for the current active Issue.
   - Do not run `issue start` for a different Issue while the current active Issue is unresolved.
3. Select the next Issue from existing dependency state.
   - Use the Epic plan, current projections, and `./spec-dock/scripts/spec-dock deps check <issue-id>` to identify ready Issues.
   - If no Issue is ready but the Epic plan explicitly has no executable Issue work, continue to the no-op Epic completion evidence path instead of creating unnecessary Issues.
   - If no Issue is ready and executable Issue work remains, record blocker evidence, dependency/check output, and the next human or planning action; stop and escalate instead of implementing.
   - If multiple Issues are ready, choose exactly one by dependency order, priority, and risk. Do not default to parallel execution.
4. Start the selected ready Issue through the lifecycle command.
   - Run or route `./spec-dock/scripts/spec-dock issue start <issue-id>` before Issue planning or execution.
   - Treat `active set` as recovery/manual only; do not use it as the normal Epic execution path.
5. Route the active Issue to the correct owner.
   - Missing, stale, unreviewed, template-only, or non-executable Issue requirement/design/plan -> `spec-dock-issue-planning`.
   - Approved, reviewer-pass, executable Issue plan -> `spec-dock-issue-execution`.
   - If execution exposes a spec gap, return to Issue planning or clarification; do not invent assumptions in Epic execution.
6. After Issue final local gates, route PR delivery and merge preparation.
   - Hand off to `github-pr-merge-preparer` for PR creation/reuse, observation, repair loop coordination, and merge-prepared evidence.
   - If PR preparation is blocked, stale, limited, or returns a human gate, preserve that evidence and stop; do not claim merge readiness.
7. Return to `workflow_issue.md` for `issue finish` evaluation.
   - After `github-pr-merge-preparer` returns merge-prepared evidence or a blocked result, use `spec-dock/docs/workflow_issue.md` to decide whether `./spec-dock/scripts/spec-dock issue finish` may run.
   - This skill does not claim reviewer pass, issue finish, delivery completion, PR merge readiness, or GitHub closure.
8. Repeat one Issue at a time until the Epic has no remaining executable Issue work.
   - For a small or no-op Epic with no executable Issue work, record completion evidence, skipped-work rationale, and the Epic-level gate instead of creating unnecessary Issues.
   - When all Issues are complete or intentionally skipped, use the Epic workflow's Epic-level completion gate and PR handoff expectations.

## Stop Conditions

- Active Issue exists and needs continuation, finish evaluation, or user decision.
- Active Epic or reviewed Epic planning handoff is missing after requested-Epic resolution.
- Dependency state is stale, unavailable, or says no Issue is ready while executable Issue work remains.
- Multiple ready Issues exist but dependency/priority/risk cannot justify a single next Issue.
- Selected Issue cannot be started through `issue start`.
- Issue specs are missing, stale, unreviewed, or not executable.
- PR preparation returns blocked, stale-head, unresolved review-thread limitation, failed checks, merge conflict, permission/auth, timeout, or human-gate evidence.
- Any route would require runtime command changes, dependency algorithm changes, PR merge/auto-merge, GitHub issue close, reviewer-pass self-claim, issue-finish self-claim, or replacing existing skills.

## Explicit Non-Goals

- Do not change runtime commands or dependency algorithms.
- Do not replace `spec-dock-epic-planning`, `spec-dock-issue-planning`, `spec-dock-issue-execution`, or `github-pr-merge-preparer`.
- Do not create unnecessary Issues for a no-op/small Epic.
- Do not merge PRs, enable auto-merge, close GitHub issues, resolve review threads, dismiss reviews, or mutate GitHub state beyond the delegated skills' existing contracts.
- Do not claim reviewer pass, issue finish, merge-prepared status, PR merge, or Epic completion without the workflow-owned evidence and gates.
