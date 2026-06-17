# PR repair unit U007: active set raw preflight

## Scope

Repair PR #194 review comment 3426282934 for issue `iss-00193`.

## Problem

`active set` validates compiled issue dependencies before marking a scope active, but raw node dependencies between empty initiatives/epics can form a cycle that disappears from the compiled issue map. This contradicts the Option A requirement: raw node-level cycles must be blocked before a workflow proceeds from invalid state.

## Required Change

- Add raw node dependency validation preflight to the active selection path before readiness succeeds.
- Use the existing dependency topology reader resolution surface when available:
  - `load_node_dependency_resolutions(specdock_dir, graph)`
  - `validate_raw_node_dependency_graph(graph, raw_node_depends_on_map)`
- Preserve optional-port compatibility for tests or adapters that do not expose raw node resolution.
- Keep existing compiled issue dependency validation and readiness behavior.

## Expected Tests

- Add or update focused tests proving `active set` rejects a raw empty-container cycle even when compiled issue dependencies are empty.
- Keep existing active-selection behavior passing.

## Completion Evidence

- Changed files listed by the implementer.
- Focused tests pass.
- `git diff --check` passes.
