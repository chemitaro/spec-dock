---
name: spec-dock-issue-execution
description: Execute an active spec-dock issue while keeping spec-dock/docs/workflow_issue.md as the source of truth.
---

# Spec-Dock Issue Execution

Use this skill only for active issue execution after planning handoff readiness is established. It is a concise reminder for issue execution.

This skill is a fixed kernel. It must not carry state-specific generated Runbook text, full profile procedure sets, or issue-local workflow projections.

## First-Read Handoff

- First ask the runtime for current execution guidance:
  - `./spec-dock/scripts/spec-dock guidance issue-execution`
- Treat the command stdout as current guidance only. It is not canonical authority, and must not be edited as source of truth.
- Register the returned `state`, `next_action`, `reason_code`, `authority`, `may_execute_approved_plan`, commands, and stop conditions in your task checklist before acting.
- Do not expect or derive the current implementation step, worker, reviewer, verification, or context packet from runtime guidance. Read execution order and step obligations from the approved `plan.md`, and record observed evidence in `report.md`.
- If runtime guidance cannot be generated, is malformed, or contradicts canonical docs, stop and fall back to `spec-dock/docs/workflow_issue.md` and the active issue docs instead of guessing the next step.
- Generated projections such as `spec-dock/.agent/runbooks/current-runbook.*` or `spec-dock/active/current-runbook.*` are ignored human/debug output. Do not read, edit, or manage them as handoff authority.

## Canonical Fallback

- Source of truth: `spec-dock/docs/workflow_issue.md`.
- Planning / execution contract: active issue `requirement.md`, `design.md`, `plan.md`, and `report.md`.
- Clarification fallback: `spec-dock/docs/workflow_clarification.md`.
- Behavior-first and test-case semantics: `spec-dock/docs/phase_plan_issue.md` and `spec-dock/docs/authoring/issue-plan.md`.
- For planned executable workflow contract / command queue details, concrete `具体テストケース一覧`, report evidence destination, and amendment trigger rules, use `spec-dock/docs/authoring/issue-plan.md` and the active `plan.md`.

## Stop Conditions And Authority

- Start execution only after `requirement.md`, `design.md`, and `plan.md` are approved / reviewer-pass and recorded as ready under the issue workflow.
- Treat requirement / design / plan creation or repair as planning / spec authoring work, not issue execution work.
- Stop if any artifact is draft, template-only, unresolved, stale, contradictory, or missing reviewer-pass evidence.
- Stop on any unresolved spec gap; return to `spec-dock/docs/workflow_clarification.md` instead of absorbing the gap inside execution.
- Stop if active context, allowed paths, acceptance criteria, reviewer requirements, delegated worker boundaries, or closure conditions cannot be verified.
- Execute exactly one current implementation step at a time. Do not start implementation, review, or commit work for the next step until the current step is closed.
- Treat `plan.md` as the planned executable workflow contract / command queue. A non-executable `plan.md` is a planning gap, not an execution assumption.
- Treat a non-executable `plan.md` as an unresolved plan gap.
- If implementation reveals an unresolved requirement / design / plan gap, return to planning / spec authoring or clarification instead of inventing an execution assumption.
- Use `authorized_profile` as the obligation authority when the Runbook reports profile data. `lite_candidate` is not authority and must not reduce obligations by itself.
- Treat unavailable tooling, denied access, host conflicts, waiver requests, degraded mode, and similar blockers as stop/incomplete unless `workflow_issue.md` explicitly says otherwise. They are not reviewer passes or normal implementation success.

## Delegation And Evidence

- Keep the parent agent responsible for orchestration, context, acceptance evidence, and final closure. Delegates may implement bounded tasks, but they do not own the issue.
- Keep normal file mutation delegated. Route runtime, tests, and scaffold behavior to `dev-coder`. Route shipped docs, templates, skills, and workflow text to `doc-writer`.
- Parent direct implementation or direct reviewer-fail fixes require a documented Parent Implementation Exception before mutation.
- Treat `report.md` as the observed evidence ledger for actual Red / Green / Refactor results, verification output, discovered tests, closure delta, reviewer verdicts, and commit/no-op evidence.
- Treat `report.md` as the canonical `Spec Interpretation / Decision Ledger` for material implementation-time interpretation, decisions, deviations, tradeoffs, open questions, and promotion / follow-up. Do not store worker raw transcripts, private reasoning, or secrets there.
- Keep the feedback loop grounded in public interface / observable behavior, reproduction evidence, and the approved `plan.md` contract.
- Require delegated workers to return a `Ledger Note` when they encounter material interpretation, decision, deviation, tradeoff, open question, or follow-up. The minimum fields are `source-agent`, `topic`, `trigger`, `ambiguity / constraint`, `observed facts`, `options considered`, `proposed decision`, `rationale`, `affected files`, `affected tests`, `risk if wrong`, `rollback or revisit`, `confidence`, and `needs orchestrator decision`.
- Require workers with no material decision to state `No material implementation decisions beyond the approved plan.` A worker `proposed decision` is not an accepted decision; the parent orchestrator must integrate, reject, defer, supersede, or promote it in the canonical report ledger.
- Before completion, ensure ledger entries have no `Status=open`; each resolved / superseded entry has disposition evidence, required follow-up / promotion evidence, and no report-only durable decision.
- When review fails, perform bounded delegated follow-up and rerun review. Parent direct fixes require a documented Parent Implementation Exception.
- After final commit gates pass, use `github-pr-merge-preparer` for final PR delivery and merge-preparation evidence before `issue finish`; keep the detailed completion policy in `workflow_issue.md`.

## Runtime Command Reminders

- Use the shipped runtime path: `./spec-dock/scripts/spec-dock ...`.
- Normal lifecycle is `issue start <target>` before execution and `issue finish` only after the workflow completion gates pass.
- `issue start -f` / `issue start --force` bypasses only the unfinished-active-issue guard; it does not bypass readiness, target validation, or checkout safety.
- After `issue finish`, avoid `sync` on the just-finished issue branch when active clear must remain clear.
- Mutate dependencies command-first with `deps add`, `deps remove`, and `deps check`: `./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>`, `./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>`, and `./spec-dock/scripts/spec-dock deps check <target>`.
- Evidence commands include `validate` and `sync`: `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync`.
- Use `--no-github` only for explicit cache/local verification without GitHub calls.
- Step completion still requires required verification, a fresh step reviewer pass, the Step Commit Gate, and a post-commit clean check as defined by `workflow_issue.md`.

## Kernel Boundary

Do not copy the full workflow here; update `workflow_issue.md` when execution policy changes.
