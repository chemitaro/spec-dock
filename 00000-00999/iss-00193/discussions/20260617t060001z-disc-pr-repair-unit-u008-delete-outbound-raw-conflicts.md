# PR repair unit U008: delete outbound raw conflicts

## Scope

Repair PR #194 review comment 3426282937 for issue `iss-00193`.

## Problem

Delete conflict detection already blocks dependency edges crossing the deleted subtree boundary unless `--force`. U005 added detection for surviving raw sources that point into the deleted subtree, but raw dependencies from deleted source nodes to surviving target nodes are still skipped when the graph contains empty containers.

## Required Change

- Extend delete boundary conflict detection to include raw outbound dependencies whose source is inside the deleted subtree and whose resolved target is outside the subtree.
- Prefer `load_node_dependency_resolutions(specdock_dir, graph)` as the authoritative interpretation of raw references.
- Preserve U005 behavior for surviving-source raw refs into the deleted subtree:
  - no-force blocks before mutation;
  - force scrubs exact surviving raw refs where source survives.
- For deleted-source outbound raw refs, no-force must block; force may proceed because the source metadata is removed with the deleted subtree.
- Preserve fallback behavior for adapters without raw resolution support, limited to direct node-id handling and existing heuristic scrub.

## Expected Tests

- Add CLI regression where deleting an empty container with a raw dependency to a surviving empty container blocks without `--force`.
- Add CLI regression where the same shape succeeds with `--force`.
- Preserve existing U005 raw-ref cleanup regressions.

## Completion Evidence

- Changed files listed by the implementer.
- Focused delete tests pass.
- `git diff --check` passes.
