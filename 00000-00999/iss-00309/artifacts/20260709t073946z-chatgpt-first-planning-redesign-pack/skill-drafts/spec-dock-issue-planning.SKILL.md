---
name: spec-dock-issue-planning
description: Create SpecDock issue requirement, design, and plan artifacts through a single ChatGPT-first workflow.
---

# spec-dock-issue-planning

## Purpose

Create canonical Issue `requirement.md`, `design.md`, and `plan.md` through one ChatGPT-first workflow.

## Route

1. Read active Issue context and parent context.
2. Classify the input context shape.
3. Compose a ChatGPT-first planning request.
4. Ask ChatGPT to produce canonical Issue artifacts or `information_insufficient`.
5. Review the output before adoption.
6. Proceed to execution only after reviewer-gated readiness.

## Input Context Types

These are context framing labels, not workflow modes.

| Type | Meaning |
|---|---|
| `requirement-heavy` | Requirement is mostly clear; design and plan expansion are primary. |
| `draft-heavy` | Draft R/D/P artifacts exist; formalization and refresh are primary. |
| `context-heavy` | Background, artifacts, code, or discussion logs exist; requirement extraction is primary. |

The final output contract is identical for all three types.

## Required Artifacts

- `requirement.md`
- `design.md`
- `plan.md`
- Optional supporting artifacts when useful.

## Information Insufficient

If the provided context cannot support formal Issue planning, return `information_insufficient` with missing information and human questions.

## Adoption Review

Check:

- canonical R/D/P are all present;
- draft artifacts are refreshed against current repository state;
- prior completed Issues and dependency state are considered;
- unresolved ledgers are not ignored;
- no separate workflow modes are introduced for different input sources;
- execution is not allowed from draft-only output.

## Fallback

Use manual Issue Planning only after explicit human approval for emergency fallback.
