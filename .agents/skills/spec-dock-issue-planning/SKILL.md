---
name: spec-dock-issue-planning
description: Actor-based issue requirement, design, and plan authoring workflow spine for spec-dock.
---

# Spec-dock Issue Planning

Use this skill for issue planning work: create or update issue-level requirement/design/plan docs, prepare review readiness, or return unresolved execution gaps to authoring.

This skill is a fixed kernel. It must not carry state-specific generated Runbook text, full profile procedure sets, or issue-local workflow projections.

## First-Read Handoff

- First ask the runtime for the current planning Runbook:
  - `./spec-dock/scripts/spec-dock workflow next issue-planning`
- Treat the generated Runbook as current guidance only. It is not canonical authority, and must not be edited as source of truth.
- If the runtime Runbook cannot be generated, is malformed, or contradicts canonical docs, stop and fall back to the canonical docs below instead of guessing the next phase.
- Generated projections such as `spec-dock/.agent/runbooks/current-runbook.*` or `spec-dock/active/current-runbook.*` are ignored output. Do not edit them as canonical artifacts.

## Canonical Fallback

- Primary lifecycle / execution workflow: `spec-dock/docs/workflow_issue.md`.
- Spec authoring workflow: `spec-dock/docs/workflow_spec_authoring.md`.
- Clarification workflow for unresolved ambiguity, interview evidence, and source-grounded questions: `spec-dock/docs/workflow_clarification.md`.
- Issue plan phase playbook: `spec-dock/docs/phase_plan_issue.md`.
- Issue plan field semantics and executable step schema: `spec-dock/docs/authoring/issue-plan.md`.
- Decision routing examples and detailed placement guidance: `spec-dock/docs/authoring/decision-routing.md`.

## Stop Conditions And Authority

- Stop if active context, artifact freshness, reviewer pass evidence, or delegated draft adoption evidence is missing, stale, failed, unavailable, denied, waived, provisional, or contradictory.
- Stop if `requirement.md`, `design.md`, or `plan.md` is template-only, unresolved, or not reviewer-passed for the current phase.
- Stop if planning reveals unresolved requirement / design / plan gaps; route back to `spec-dock/docs/workflow_clarification.md` or the relevant authoring phase.
- Keep canonical `requirement.md` / `design.md` / `plan.md` / `report.md` main-orchestrator-owned. This skill does not grant delegated canonical write authority.
- `system-architect` and `implementation-planner` are delegated agent roles only; their drafts are scope-local evidence only and do not replace main orchestrator adoption, fresh `spec-reviewer` pass, phase promotion, or execution handoff readiness.
- Delegated drafts, research, discussions, and generated Runbooks are evidence only until adopted into canonical artifacts and recorded in `report.md`.
- Fresh means the current artifact candidate was reviewed after its latest substantive change and fresh `spec-reviewer` returns `review_status: pass`.
- Record Spec Authoring Gate evidence in `report.md` when canonical artifacts are promoted or execution handoff readiness changes.

## Kernel Boundary

- Use the runtime Runbook and canonical docs for phase-specific procedure details; do not copy the full workflow here.
- Keep only durable entrypoint, authority, freshness, fallback, and stop-condition reminders in this skill.
