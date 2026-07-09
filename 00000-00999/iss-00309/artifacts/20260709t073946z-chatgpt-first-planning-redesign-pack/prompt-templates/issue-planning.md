# Issue Planning prompt template

## Instruction

Create canonical Issue planning artifacts from the provided input context.

## Input Context Type

Use one of:

- `requirement-heavy`
- `draft-heavy`
- `context-heavy`

This is context framing only. It is not a workflow mode and must not change the required output.

## Required Output

```text
issue/requirement.md
issue/design.md
issue/plan.md
issue/artifacts/review-focus.md
```

## Requirements

- Produce canonical Issue `requirement.md`, `design.md`, and `plan.md`.
- Refresh drafts against current repository state, prior completed Issues, dependency state, and unresolved ledgers.
- Select an appropriate implementation quality-gate intensity in the plan when needed.
- Return `information_insufficient` if formal planning would require guessing.
- Do not introduce separate workflow modes for different input sources.
