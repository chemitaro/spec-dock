# Epic Planning prompt template

## Instruction

Create or refresh Epic planning artifacts and draft child Issue artifacts.

## Required Output

```text
epic/requirement.md
epic/design.md
epic/plan.md
epic/artifacts/issue-slicing.md
epic/artifacts/dependency-map.md
issues/<issue-id>/draft-requirement.md
issues/<issue-id>/draft-design.md
issues/<issue-id>/draft-plan.md
```

## Requirements

- Slice Issues with clear boundaries and dependency order.
- Treat child Issue drafts as handoff artifacts, not canonical Issue planning.
- Add a final child Issue for Epic quality gate and mergeable PR delivery for Multi-Issue implementation Epics.
- Include skip rationale if a separate final quality Issue is unnecessary.
- Return `information_insufficient` when slicing would be speculative.
