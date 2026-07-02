---
name: spec-dock-epic-execution
description: First-read coordinator for executing a planned spec-dock Epic through one Issue at a time, routing to existing Issue planning, Issue execution, PR preparation, and completion gates.
---

# Spec-Dock Epic Execution

Use this skill after Epic planning is complete and the Epic requirement, design, and plan are reviewer-gated for downstream Issue work. Read the Epic report as an evidence ledger for unresolved blockers, decisions, and handoff state; do not treat it as a reviewer-gated planning artifact. This skill is a coordinator only; it is not a semantic reviewer. Keep detailed lifecycle rules in `spec-dock/docs/workflow_epic.md`, `spec-dock/docs/workflow_issue.md`, and the existing leaf skills.

## Workflow-Scoped Authorization

- A user request to use a SpecDock workflow is explicit workflow-scoped authorization to use the SpecDock-defined named sub-agents and reviewers required by that workflow.
- Do not ask for additional per-role or per-phase permission before invoking SpecDock-defined named roles within the active repo/worktree, active SpecDock scope, current session, and documented role responsibility.
- Ask the user only for scope expansion, destructive actions, external publishing, credentialed external mutation, private external systems, or roles outside the SpecDock workflow.
- ユーザーが SpecDock workflow の利用を依頼した場合、その依頼自体を、SpecDock が定義する named sub-agent / reviewer を workflow に従って利用する明示的な許可として扱う。
- active repo/worktree、active SpecDock scope、current session、documented role responsibility の範囲内では、role ごと・phase ごとの追加承認を求めない。
- scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途確認する。

## First-Read Coordinator Flow

1. Bootstrap current state.
   - Resolve an explicitly requested Epic to the active Epic, or route the required lifecycle activation / selection step before applying active-Epic checks.
   - Confirm the active Epic and read its reviewer-gated `requirement.md`, `design.md`, and `plan.md`, plus `report.md` as an evidence ledger for unresolved blockers, decisions, and handoff state.
   - Read the downstream Issue handoff package: Issue list, dependency order, responsibility boundaries, draft artifact path index or skip evidence, expected verification, reviewer focus, delegation contract, and any unresolved / stale report entries.
   - Check `./spec-dock/scripts/spec-dock active show` for an active Issue.
   - Check git/projection/GitHub freshness as needed for the user's request, using `sync`, `sync --github`, `validate`, `git status`, `git fetch`, or GitHub inspection when stale state could affect Issue readiness or PR delivery.
   - If no active Epic remains after requested-Epic resolution, or no reviewed Epic planning handoff exists, stop and route back to `spec-dock-epic-planning` or the Epic workflow.
2. If an active Issue already exists, stop before selecting another Issue.
   - Require a continuation, finish evaluation, or explicit user decision for the current active Issue.
   - Do not run `issue start` for a different Issue while the current active Issue is unresolved.
3. Select the next Issue from existing dependency state.
   - Use the Epic plan, current projections, and `./spec-dock/scripts/spec-dock deps check <issue-id>` to identify ready Issues.
   - Distinguish `handoff-ready` from `execution-ready`: handoff-ready means the Issue may enter Issue planning; execution-ready means Issue planning has composed canonical docs, passed fresh review, and produced an executable plan.
   - If no Issue is ready but the Epic plan explicitly has no executable Issue work, continue to the no-op Epic completion evidence path instead of creating unnecessary Issues.
   - If no Issue is ready and executable Issue work remains, record blocker evidence, dependency/check output, and the next human or planning action; stop and escalate instead of implementing.
   - If multiple Issues are ready, choose exactly one by dependency order, priority, and risk. Do not default to parallel execution.
4. Start the selected ready Issue through the lifecycle command.
   - Run or route `./spec-dock/scripts/spec-dock issue start <issue-id>` before Issue planning or execution.
   - Treat `active set` as recovery/manual only; do not use it as the normal Epic execution path.
5. Route the active Issue to the correct owner.
   - Missing, stale, unreviewed, template-only, or non-executable Issue requirement/design/plan -> `spec-dock-issue-planning`.
   - Approved, reviewer-pass, executable Issue plan -> `spec-dock-issue-execution`.
   - Issue-local `draft-design` / `draft-plan` handoff evidence is created with `./spec-dock/scripts/spec-dock new artifact draft-design --issue <issue-id>` and `./spec-dock/scripts/spec-dock new artifact draft-plan --issue <issue-id>`. `assurance compose` is canonical compose only; do not invent actor-, specialist-, or depth-specific draft commands.
   - If execution exposes a spec gap, return to Issue planning or clarification; do not invent assumptions in Epic execution.
   - Fresh reviewer passes required by the routed workflow are gates and must not be skipped while waiting for extra permission inside the bounded SpecDock workflow scope.
6. After Issue final local gates, route PR delivery and merge preparation when the Epic plan requires per-Issue PR delivery.
   - For normal workflows, hand off to `github-pr-merge-preparer` for PR creation/reuse, observation, repair loop coordination, and merge-prepared evidence.
   - If the reviewed Epic plan intentionally runs Issues one by one without per-Issue PR and reserves final PR delivery for a final quality Issue such as `iss-00276`, require the intermediate Issue report to contain the `workflow_issue.md` deferred PR delivery gate evidence and do not invoke PR preparation for that intermediate Issue.
   - If PR preparation is blocked, stale, limited, or returns a human gate, preserve that evidence and stop; do not claim merge readiness.
7. Return to `workflow_issue.md` only after merge-prepared evidence.
   - If PR delivery is intentionally deferred by the reviewed Epic plan, return to `workflow_issue.md` only after the intermediate Issue has deferred PR delivery gate evidence. That gate must identify the final quality Issue, dependency edge, no-per-Issue-PR rationale, no merge-prepared claim before final PR delivery, and reviewer-confirmed local completion / issue finish conditions.
   - If `github-pr-merge-preparer` returns blocked, stale, limited, or human-gate evidence, preserve that terminal PR-preparation evidence and stop; do not run `issue finish`.
   - Only after `github-pr-merge-preparer` returns merge-prepared evidence, use `spec-dock/docs/workflow_issue.md` to decide whether `./spec-dock/scripts/spec-dock issue finish` may run.
   - This skill does not claim reviewer pass, issue finish, delivery completion, PR merge readiness, or GitHub closure.
8. Repeat one Issue at a time until the Epic has no remaining executable Issue work.
   - For a small or no-op Epic with no executable Issue work, record completion evidence, skipped-work rationale, and the Epic-level gate instead of creating unnecessary Issues.
   - When all Issues are complete or intentionally skipped, use the Epic workflow's Epic-level completion gate and PR handoff expectations.

## Structural Blockers And Reviewer Findings

- Treat structural blockers as fail-closed readiness defects: missing canonical docs, missing or stale reviewer pass, missing Issue readiness contract, missing executable plan structure, missing delegation contract, missing verification, missing reviewer focus, unresolved blocking / stale report entries, raw artifact authority, decision-only execution-ready, or missing specialist / fallback evidence where the Issue grade requires it.
- Treat reviewer findings as semantic or quality concerns where the required structure exists but sufficiency is doubtful, such as weak acceptance criteria, incomplete test strategy, thin adoption rationale, or minor Japanese-first wording drift.
- Do not replace `spec-reviewer` with this coordinator. Route semantic reviewer concerns to the appropriate reviewer or planning workflow and preserve the finding evidence.
- Japanese-first applies during readiness and execution for docs, `report.md`, and artifacts. Use Japanese body text first; keep exact identifiers, commands, paths, and reviewer role names unchanged.

## Stop Conditions

- Active Issue exists and needs continuation, finish evaluation, or user decision.
- Active Epic or reviewed Epic planning handoff is missing after requested-Epic resolution.
- Dependency state is stale, unavailable, or says no Issue is ready while executable Issue work remains.
- Multiple ready Issues exist but dependency/priority/risk cannot justify a single next Issue.
- Selected Issue cannot be started through `issue start`.
- Issue specs are missing, stale, unreviewed, not executable, or only handoff-ready when execution-ready is required.
- Structural blocker evidence exists in Epic or Issue docs, handoff package, reviewer gates, delegation contract, verification contract, or report ledger.
- PR preparation returns blocked, stale-head, unresolved review-thread limitation, failed checks, merge conflict, permission/auth, timeout, or human-gate evidence.
- Any route would require runtime command changes, dependency algorithm changes, PR merge/auto-merge, GitHub issue close, reviewer-pass self-claim, issue-finish self-claim, or replacing existing skills.

## Explicit Non-Goals

- Do not change runtime commands or dependency algorithms.
- Do not replace `spec-dock-epic-planning`, `spec-dock-issue-planning`, `spec-dock-issue-execution`, or `github-pr-merge-preparer`.
- Do not create unnecessary Issues for a no-op/small Epic.
- Do not merge PRs, enable auto-merge, close GitHub issues, resolve review threads, dismiss reviews, or mutate GitHub state beyond the delegated skills' existing contracts.
- Do not claim reviewer pass, issue finish, merge-prepared status, PR merge, or Epic completion without the workflow-owned evidence and gates.
