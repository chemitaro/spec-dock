# PR repair unit U010: delete raw resolution fail closed

## Scope

Repair PR #194 review comment 3426476954 for issue `iss-00193`.

## Problem

Delete now uses `load_node_dependency_resolutions` to detect raw dependency boundary conflicts involving empty containers. However, if that resolver raises for any raw dependency, the current helper drops the resolver output and falls back to literal node-id scanning. That fallback cannot detect GitHub number, scoped, or URL raw references and can allow destructive delete to proceed with unresolved dependency state.

## Required Change

- Do not ignore exceptions from `load_node_dependency_resolutions` during delete preflight.
- Fail closed before local delete mutation when raw dependency resolution fails.
- Reuse the existing dependency topology load failure result shape if possible, so callers receive a non-ok preflight failure with recovery guidance.
- Preserve literal node-id fallback only for adapters that do not expose `load_node_dependency_resolutions`.
- Preserve U005/U008 behavior when raw resolution succeeds.

## Expected Tests

- Add a focused delete regression where `load_node_dependency_resolutions` raises and delete returns a non-ok topology/metadata validation failure before deleting local nodes.
- Verify no local delete mutation and no dependency scrub mutation occur in that failure path.
- Preserve existing delete raw-ref cleanup and outbound conflict regressions.

## Completion Evidence

- Changed files listed by the implementer.
- Focused delete tests pass.
- `git diff --check` passes.
