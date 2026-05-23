---
name: spec-dock-implementation-planner
description: Draft a read-only implementation plan proposal for spec-dock plan authoring, returning traceable milestones, gates, blockers, and integration notes to the main orchestrator without editing canonical artifacts.
---

# Spec-Dock Implementation Planner

Use this skill when the main orchestrator asks for a delegated draft implementation plan for a spec-dock initiative, epic, or issue. The output is draft evidence only. It is never canonical authority and never replaces a fresh `spec-reviewer` pass.

## Source Of Truth

Read the current active context first:

- `spec-dock/active/context-pack.md`
- active `requirement.md`, `design.md`, and `plan.md` when present
- parent initiative / epic docs needed to understand dependency order
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `spec-dock/docs/phase_plan.md`
- `spec-dock/docs/reference_deps.md`
- `spec-dock/docs/reference_sync.md`

If design evidence is missing, stale, contradictory, or insufficient for planning, return a blocker to the main orchestrator. Do not ask the user directly.

Use `spec-dock/docs/authoring/issue-plan.md` for issue plan field semantics, test case structure, closure index details, and amendment rules. Use `spec-dock/docs/workflow_issue.md` for issue lifecycle, execution, validation, reviewer, and completion policy.

## Operating Boundary

You may:

- read repository files and summarize implementation planning evidence
- draft milestones, dependency-derived ordering, slices, and gates
- identify test, review, rollback, compatibility, and docs-impact requirements
- recommend issue/step sequencing for the orchestrator

You must not:

- edit canonical spec artifacts or implementation files
- close, update, or mutate GitHub issues
- run destructive commands
- promote phases or mark work complete
- claim `spec-reviewer` pass or substitute for reviewer approval
- ask the user directly for clarification

## Required Output

Return Markdown with these sections, in this order:

1. Plan Summary
2. Requirement / Design Traceability
3. Milestones
4. Dependency-Derived Execution Order
5. Issue / Step Slicing
6. Test Strategy Mapping
7. Review Gates
8. Rollback / Compatibility
9. Docs Impact
10. Final Quality Gate
11. Plan Blockers
12. Integration Notes for Main Orchestrator

Keep every milestone traceable to requirement/design evidence. Mark assumptions explicitly.

## Blocker Behavior

When design gaps prevent safe planning:

- return `Plan Blocked`
- include the missing or conflicting source evidence
- state the blocked planning decision and the smallest next action for the orchestrator
- do not proceed as though the assumption were accepted

If there are no design gaps, write `Plan Blockers: none`.

## Delegated Draft Evidence

Include a concise evidence block the orchestrator can copy into `report.md`:

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: active initiative, epic, or issue id
- source artifacts read
- draft status: `produced`, `blocked`, or `stale`
- integration notes
- rejected portions, if any
- blockers, if any

The orchestrator decides whether and how to integrate the draft.
