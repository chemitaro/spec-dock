---
name: spec-dock-issue-planning
description: Leaf skill for Issue-level requirement, design, plan authoring, draft adoption, reviewer-gated readiness, and execution handoff in SpecDock.
---

# Spec-Dock Issue Planning

Use this skill for Issue planning: create or update Issue-level `requirement.md` / `design.md` / `plan.md`, adopt or reject pre-start draft evidence, prepare fresh reviewer gates, or return unresolved execution gaps to authoring.

This skill is a fixed kernel / operational kernel. Do not copy full profile procedures, generated Runbooks, or issue-local workflow projections here.

state-specific generated Runbook text is runtime guidance. It is not canonical authority, must not be edited as source of truth, and must not replace canonical docs.

ChatGPT-first primary route: for non-trivial Issue planning, use `spec-dock-chatgpt-authoring` as the primary evidence-production route for a single Issue planning workflow. Treat `requirement-heavy`, `draft-heavy`, and `context-heavy` as input context framing only; the output contract is always canonical `requirement.md`, `design.md`, and `plan.md`, or an `information_insufficient` stop. If ChatGPT/browser/backend capacity is busy, wait and retry; if automation is unhealthy, recover or restart the browser/backend and retry. Do not switch to manual planning for queued tabs, retryable timeouts, stale sync, or fixable prompt/backend setup.

Manual backup route: use `spec-dock-issue-planning-manual` only after hard / unrecoverable ChatGPT route failure and explicit human approval. Record the failure class, recovery attempts, approval evidence, and manual-route decision in Issue `report.md`.

ChatGPT authoring relationship: `spec-dock-chatgpt-authoring` may provide Issue draft artifacts, ZIP/tree evidence, validation reports, or candidate summaries. Those outputs are evidence-only until Issue planning adopts or rejects specific claims in `report.md`, updates canonical Issue docs, and obtains a fresh `spec-reviewer` pass.

## Read First

- Runtime guidance: `./spec-dock/scripts/spec-dock guidance issue-planning`
  - Treat stdout as current guidance, not canonical authority.
  - Record `state`, `next_action`, `reason_code`, `authority`, commands, and stop conditions before acting.
  - Register the returned `state`, `next_action`, `reason_code`, `authority`, commands, and stop conditions before acting.
- Canonical docs and active artifacts:
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/authoring/decision-routing.md`
  - `spec-dock/docs/authoring/scope-layering.md`
  - active Issue `requirement.md`, `design.md`, `plan.md`, `report.md`, and scope-local `artifacts/`

## Operating Spine

1. Confirm active Issue and planning phase.
   - If runtime guidance is malformed, unavailable, or contradicts canonical docs, stop and fall back to docs plus active artifacts.
   - Ignore generated projections such as `spec-dock/.agent/runbooks/current-runbook.*` and `spec-dock/active/current-runbook.*` as authority.
   - Do not expect or derive canonical docs from `current-runbook.*`; Do not read, edit, or manage them as handoff authority.
2. Confirm Issue grade and obligation.
   - Read the Issue grade matrix in `workflow_spec_authoring.md` before creating or updating canonical docs.
   - `authorized_profile` is template/guidance/obligation authority.
   - Lite is not an automatic default; unknown or ambiguous grade/scope/impact/reviewer obligation escalates to Standard or higher.
3. Treat drafts as evidence, not authority.
   - Pre-start `draft-design`, `draft-plan`, delegated drafts, research, discussions, and generated Runbooks remain evidence until adopted.
   - Adoption or rejection must be reflected in `report.md` and the relevant canonical docs.
   - `system-architect` and `implementation-planner` outputs never replace main-orchestrator adoption, fresh `spec-reviewer` pass, phase promotion, or execution handoff readiness.
   - For draft-heavy input context, refresh current repo state, dependency state, prior completed Issues, unresolved ledgers, and drift evidence before promoting any draft claim.
   - If drift is Issue-local, repair it in Issue planning; if it changes Epic boundaries, Issue order, or scope allocation, return to Epic planning repair or clarification.
4. Author phases in order.
   - Requirement, design, and plan each need a fresh `spec-reviewer` `review_status: pass` after the latest substantive change.
   - Record Spec Authoring Gate evidence in `report.md` whenever canonical artifacts are promoted or execution handoff readiness changes.
5. Produce execution handoff only when ready.
   - Execution-ready requires reviewer-passed canonical docs, executable `plan.md`, required verification/delegation/reviewer-focus evidence, adopted draft evidence, and no unresolved report-ledger blockers.
   - Handoff-ready evidence from Epic planning is not execution-ready by itself.

## Issue Planning Input Context

Issue Planning uses one workflow. The following labels describe the dominant input context, not separate workflow modes:

- `context-heavy`: start from user discussion, repo docs/code, artifacts, ADRs, and current active scope. Use ChatGPT-first evidence for non-trivial scope, then author canonical `requirement.md`, `design.md`, and `plan.md` in order; each promotion needs fresh `spec-reviewer` evidence.
- `requirement-heavy`: start from an approved, human-authored, or otherwise source-grounded `requirement.md` candidate. Use ChatGPT-first evidence for design/plan options when non-trivial, then create canonical `design.md` and `plan.md` from that requirement; route gaps or contradictions back to requirement authoring or clarification.
- `draft-heavy`: start from Issue-local draft requirement/design/plan evidence from Epic planning, delegated planning, or `spec-dock-chatgpt-authoring`. Refresh current state and prior Issue outcomes, record Evidence Adoption Ledger entries for adopted and rejected draft claims, update canonical docs only through the main orchestrator, and obtain a fresh `spec-reviewer` pass before execution handoff.

Do not split Issue Planning into separate modes based on input source. Different inputs affect context framing and review focus only; they do not change the canonical artifact contract or reviewer gates.

## Contract Anchors

- Use this skill for issue planning work: create or update issue-level requirement/design/plan docs while keeping canonical docs main-orchestrator-owned.
- Delegated authoring is scope-local evidence only and does not grant delegated canonical write authority.
- fresh `spec-reviewer` returns `review_status: pass`; record Spec Authoring Gate evidence before handoff.
- Stop if planning authority, freshness, reviewer gates, draft adoption, or execution handoff readiness cannot be verified.

## Stop Conditions

- Active context is missing, stale, or inconsistent.
- Runtime guidance, canonical docs, active artifacts, or `authorized_profile` disagree and the conflict cannot be resolved locally.
- Issue grade, scope, impact, or reviewer obligation is missing or ambiguous without escalation evidence.
- `requirement.md`, `design.md`, or `plan.md` is template-only, unresolved, stale, contradictory, or lacks fresh reviewer pass for the current phase.
- Draft adoption evidence or Evidence Adoption Ledger entries are missing, stale, failed, unavailable, denied, waived, provisional, or contradictory.
- Draft-heavy input is being used to bypass canonical adoption, fresh `spec-reviewer`, or execution handoff gates.
- ChatGPT-first route has a retryable, recoverable, waiting, or setup failure and manual backup has not been explicitly approved by the user.
- Planning exposes unresolved requirement / design / plan gaps; route to clarification or the relevant authoring phase instead of execution.

## Kernel Boundary

- Keep detailed profile procedures in docs and templates.
- Keep only durable entrypoint, authority, freshness, fallback, draft handling, and stop-condition reminders here.
