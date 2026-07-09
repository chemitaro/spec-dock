---
name: spec-dock-initiative-planning
description: Create SpecDock initiative planning artifacts through the ChatGPT-first route.
---

# spec-dock-initiative-planning

## Purpose

Create or refresh Initiative-level planning artifacts using ChatGPT-first planning as the primary route.

## Route

1. Read the active Initiative context and relevant artifacts.
2. Use `spec-dock-chatgpt-authoring` to compose a ChatGPT-first planning request.
3. Ask ChatGPT for Initiative `requirement.md`, `design.md`, `plan.md`, and Epic decomposition context.
4. Review the output before adoption.
5. Preserve human approval before creating or committing Epic slices.

## Required Inputs

- Initiative goal or existing Initiative artifacts.
- Repository and branch.
- GitHub sync state or explicit lower-authority local context.
- Operator intent.
- Development background.
- Relevant ADRs, code state, discussion notes, or prior artifacts.

## Required Artifacts

- Initiative `requirement.md`.
- Initiative `design.md`.
- Initiative `plan.md`.
- Epic candidate list or Epic handoff context.
- Optional supporting artifacts when they reduce ambiguity.

## Information Insufficient

If Initiative scope, objective, or decomposition basis is too unclear, return `information_insufficient` and the questions needed for human clarification.

## Adoption Review

Check:

- Epic candidates have clear boundaries;
- human approval gate remains before Epic creation;
- ChatGPT output is evidence until adopted;
- manual fallback is not the default route.

## Fallback

Use manual Initiative Planning only after explicit human approval for emergency fallback.
