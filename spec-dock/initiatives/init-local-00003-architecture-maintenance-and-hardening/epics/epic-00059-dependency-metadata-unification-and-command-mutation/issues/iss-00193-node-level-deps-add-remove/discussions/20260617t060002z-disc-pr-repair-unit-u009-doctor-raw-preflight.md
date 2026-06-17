# PR repair unit U009: doctor raw preflight

## Scope

Repair PR #194 review comment 3426282941 for issue `iss-00193`.

## Problem

`doctor` can report ok for repositories where raw node dependencies between empty containers form a cycle. `validate` rejects this state after U001, so doctor must not silently pass it.

## Required Change

- Add raw node dependency validation to doctor diagnostics when the topology reader exposes `load_node_dependency_resolutions`.
- Use `validate_raw_node_dependency_graph` with the same raw node dependency map shape used by validate/sync/deps check.
- Report raw validation failures as doctor findings without removing existing graph/dependency checks.
- Preserve optional-port compatibility for adapters that do not expose raw node resolution.

## Expected Tests

- Add a focused CLI/runtime doctor regression where a raw empty-container cycle produces a doctor finding / non-ok result.
- Preserve existing doctor behavior for valid repositories.

## Completion Evidence

- Changed files listed by the implementer.
- Focused doctor tests pass.
- `git diff --check` passes.
