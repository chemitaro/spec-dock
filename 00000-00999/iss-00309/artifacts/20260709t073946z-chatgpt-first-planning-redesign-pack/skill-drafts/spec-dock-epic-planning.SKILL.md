---
name: spec-dock-epic-planning
description: Create SpecDock epic planning artifacts and draft child issue artifacts through the ChatGPT-first route.
---

# spec-dock-epic-planning

## Purpose

Create or refresh Epic planning artifacts through ChatGPT-first planning and produce draft artifacts for child Issues.

## Route

1. Read Epic context, Initiative context, and relevant artifacts.
2. Compose a ChatGPT-first planning request.
3. Ask ChatGPT to produce Epic formal artifacts plus child Issue draft artifacts.
4. Review Issue slicing before creating or updating Issues.
5. Preserve human approval at the Issue slice decision point.

## Required Artifacts

- Epic `requirement.md`.
- Epic `design.md`.
- Epic `plan.md`.
- Child Issue draft `requirement.md`.
- Child Issue draft `design.md`.
- Child Issue draft `plan.md`.
- Optional dependency map, boundary notes, ADR candidates, or review focus notes.

## Final Child Issue

Multi-Issue implementation Epics must include a final child Issue for:

- Epic quality gate;
- cross-Issue consistency review;
- integration/manual verification;
- review feedback correction;
- mergeable PR delivery.

Single-Issue, docs-only, or no-op Epics may skip a separate final quality Issue only with explicit skip rationale and completion evidence.

## Child Issue Drafts

Child Issue drafts are handoff artifacts. They are not canonical Issue planning artifacts until Issue Planning adopts or refreshes them against current repository state.

## Fallback

Use manual Epic Planning only after explicit human approval for emergency fallback.
