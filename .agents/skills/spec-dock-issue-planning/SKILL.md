---
name: spec-dock-issue-planning
description: Leaf skill for Issue-level requirement, design, plan authoring, draft adoption, reviewer-gated readiness, and execution handoff in SpecDock.
---

# Spec-Dock Issue Planning

Use this skill for Issue planning: create or update Issue-level `requirement.md` / `design.md` / `plan.md`, adopt or reject pre-start draft evidence, prepare fresh reviewer gates, or return unresolved execution gaps to authoring.

This skill is an operational kernel. Do not copy full profile procedures, generated Runbooks, or issue-local workflow projections here.

## Read First

- Runtime guidance: `./spec-dock/scripts/spec-dock guidance issue-planning`
  - Treat stdout as current guidance, not canonical authority.
  - Record `state`, `next_action`, `reason_code`, `authority`, commands, and stop conditions before acting.
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

## Stop Conditions

- Active context is missing, stale, or inconsistent.
- Runtime guidance, canonical docs, active artifacts, or `authorized_profile` disagree and the conflict cannot be resolved locally.
- Issue grade, scope, impact, or reviewer obligation is missing or ambiguous without escalation evidence.
- `requirement.md`, `design.md`, or `plan.md` is template-only, unresolved, stale, contradictory, or lacks fresh reviewer pass for the current phase.
- Draft adoption evidence is missing, stale, failed, unavailable, denied, waived, provisional, or contradictory.
- Planning exposes unresolved requirement / design / plan gaps; route to clarification or the relevant authoring phase instead of execution.

## Kernel Boundary

- Keep detailed profile procedures in docs and templates.
- Keep only durable entrypoint, authority, freshness, fallback, draft-adoption, and stop-condition reminders here.
