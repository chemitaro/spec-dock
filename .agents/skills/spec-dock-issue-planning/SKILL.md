---
name: spec-dock-issue-planning
description: Leaf skill for Issue-level requirement, design, plan authoring, draft adoption, reviewer-gated readiness, and execution handoff in SpecDock.
---

# Spec-Dock Issue Planning

Use this skill for Issue planning: create or update Issue-level `requirement.md` / `design.md` / `plan.md`, adopt or reject pre-start draft evidence, prepare fresh reviewer gates, or return unresolved execution gaps to authoring.

This skill is a fixed kernel / operational kernel. Do not copy full profile procedures, generated Runbooks, or issue-local workflow projections here.

state-specific generated Runbook text is runtime guidance. It is not canonical authority, must not be edited as source of truth, and must not replace canonical docs.

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
4. Author phases in order.
   - Requirement, design, and plan each need a fresh `spec-reviewer` `review_status: pass` after the latest substantive change.
   - Record Spec Authoring Gate evidence in `report.md` whenever canonical artifacts are promoted or execution handoff readiness changes.
5. Produce execution handoff only when ready.
   - Execution-ready requires reviewer-passed canonical docs, executable `plan.md`, required verification/delegation/reviewer-focus evidence, adopted draft evidence, and no unresolved report-ledger blockers.
   - Handoff-ready evidence from Epic planning is not execution-ready by itself.

## Issue Planning Modes

- `zero-base`: start from user discussion, repo docs/code, artifacts, and current active scope. Author `requirement.md`, `design.md`, and `plan.md` in order; each promotion needs fresh `spec-reviewer` evidence.
- `requirement-first`: start from an approved or human-authored `requirement.md`. Create `design.md` and `plan.md` from that requirement; route gaps or contradictions back to requirement authoring or clarification.
- `draft-adoption`: start from Issue-local draft requirement/design/plan evidence from Epic planning, delegated planning, or `spec-dock-chatgpt-authoring`. Record Evidence Adoption Ledger entries for adopted and rejected draft claims, update canonical docs only through the main orchestrator, and obtain a fresh `spec-reviewer` pass before execution handoff.

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
- `draft-adoption` is being used to bypass canonical adoption, fresh `spec-reviewer`, or execution handoff gates.
- Planning exposes unresolved requirement / design / plan gaps; route to clarification or the relevant authoring phase instead of execution.

## Kernel Boundary

- Keep detailed profile procedures in docs and templates.
- Keep only durable entrypoint, authority, freshness, fallback, draft-adoption, and stop-condition reminders here.
