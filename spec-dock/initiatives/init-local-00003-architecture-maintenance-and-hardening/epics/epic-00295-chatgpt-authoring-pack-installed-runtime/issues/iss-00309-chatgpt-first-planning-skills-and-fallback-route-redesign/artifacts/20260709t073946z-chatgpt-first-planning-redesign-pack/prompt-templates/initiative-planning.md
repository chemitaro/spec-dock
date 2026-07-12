# Initiative Planning prompt template

## Instruction

Create or refresh Initiative planning artifacts for SpecDock using the provided repository context and operator intent.

## Required Output

```text
initiative/requirement.md
initiative/design.md
initiative/plan.md
initiative/artifacts/epic-decomposition.md
initiative/artifacts/review-focus.md
```

## Requirements

- Define Initiative scope and non-scope.
- Identify Epic boundaries and dependencies.
- Preserve a human approval point before Epic creation.
- Return `information_insufficient` if the Initiative objective or decomposition basis is too unclear.
- Do not claim reviewer pass or execution readiness.
