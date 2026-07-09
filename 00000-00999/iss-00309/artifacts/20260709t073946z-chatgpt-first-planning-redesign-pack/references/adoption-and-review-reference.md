# Adoption and review reference

## Purpose

Define how Codex or SpecDock should review ChatGPT-generated planning artifacts before canonical adoption.

## Common Criteria

- Required artifacts exist.
- Artifact paths match expected placement.
- Requirement, design, and plan are mutually consistent.
- Scope and non-scope are explicit.
- Manual fallback is not treated as normal route.
- ChatGPT does not claim reviewer pass, assurance mutation, execution-ready, PR-ready, merge-ready, Issue finish, or Epic completion.
- `information_insufficient` is accepted when context is insufficient.

## Initiative Review

- Epic decomposition is coherent.
- Human approval point before Epic creation is preserved.
- Epic boundaries avoid obvious overlap.

## Epic Review

- Epic R/D/P are complete.
- Child Issue drafts cover the Epic without major gaps or duplication.
- Dependency order is plausible.
- Final quality / mergeable PR delivery Issue exists or skip rationale is explicit.

## Issue Review

- Issue R/D/P are canonical-quality, not merely draft summaries.
- Input context type did not reduce artifact quality.
- Drafts are refreshed against current repository state and prior Issues.
- No separate workflow-mode terminology is introduced for different input sources.

## Review Result

```yaml
status: adopted | correction_required | rejected | information_insufficient
reasons:
  - ...
required_actions:
  - ...
```
