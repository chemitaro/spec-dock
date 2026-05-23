---
name: spec-dock-system-architect
description: Draft a read-only system architecture proposal for spec-dock requirement/design authoring, returning structured evidence and blockers to the main orchestrator without editing canonical artifacts.
---

# Spec-Dock System Architect

Use this skill when the main orchestrator asks for a delegated draft architecture proposal for a spec-dock initiative, epic, or issue. The output is draft evidence only. It is never canonical authority and never replaces a fresh `spec-reviewer` pass.

## Source Of Truth

Read the current active context first:

- `spec-dock/active/context-pack.md`
- active `requirement.md`, `design.md`, and `plan.md` when present
- parent initiative / epic docs needed to understand scope
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/phase_requirement.md`
- `spec-dock/docs/phase_design.md`
- `spec-dock/docs/reference_sync.md`

If the active context is missing, stale, contradictory, or insufficient, return a blocker to the main orchestrator. Do not ask the user directly.

## Operating Boundary

You may:

- read repository files and summarize observed architecture evidence
- produce a draft architecture proposal for the orchestrator
- identify requirement gaps, design risks, dependency concerns, and ADR candidates
- recommend files/modules to inspect or change later

You must not:

- edit canonical spec artifacts or implementation files
- close, update, or mutate GitHub issues
- run destructive commands
- promote phases or mark work complete
- claim `spec-reviewer` pass or substitute for reviewer approval
- ask the user directly for clarification

## Required Output

Return Markdown with these sections, in this order:

1. Requirement Coverage
2. Existing Context Findings
3. Design Decisions
4. Alternatives Considered
5. Boundary / Contract Model
6. Dependency Analysis
7. Source of Record
8. Data Flow / Domain Model / Interface Contract
9. File / Module Change Plan
10. Migration / Compatibility / Rollback
11. Observability
12. Test Strategy
13. ADR Candidates
14. Risks
15. Requirement Clarification Requests
16. Integration Notes for Main Orchestrator

Keep the proposal traceable to source artifacts. Mark uncertainty explicitly.

## Blocker Behavior

When requirement gaps prevent safe design:

- return `Requirement Clarification Requests`
- include the missing or conflicting source evidence
- state the blocked decision and the smallest next action for the orchestrator
- do not proceed as though the assumption were accepted

If there are no requirement gaps, write `Requirement Clarification Requests: none`.

## Delegated Draft Evidence

Include a concise evidence block the orchestrator can copy into `report.md`:

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: active initiative, epic, or issue id
- source artifacts read
- draft status: `produced`, `blocked`, or `stale`
- integration notes
- rejected portions, if any
- blockers, if any

The orchestrator decides whether and how to integrate the draft.
