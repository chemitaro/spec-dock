---
種別: disc
ID: "disc-20260617t053302z-pr-repair-unit-u005-delete-raw-ref-cleanup"
タイトル: "PR #194 U005 delete raw dependency cleanup repair"
状態: "implemented"
作成者: "codex"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: ["https://github.com/chemitaro/spec-dock/pull/194", "disc-20260617t041630z-pr-repair-batch"]
authority: "proposed"
derived_from: ["/private/tmp/iss-00193-pr194-snapshot-latest/result.json"]
reflected_to: []
---

# PR #194 U005 delete raw dependency cleanup repair

## Source Finding

- Inventory: I006
- Review comment: 3425775994
- Review thread: PRRT_kwDOQ99OK86KG9yA
- Status: valid / blocking / fix-now

## Objective

Prevent a successful delete from leaving raw `depends_on` metadata references to the deleted node or its subtree, especially when the target container has no issues and therefore no compiled issue dependency edge exists.

## Scope

- Provider runtime source of truth:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py`
  - supporting infra/application contracts only if the existing delete path requires a narrow port addition
- Dogfooding runtime mirror if provider runtime source changes:
  - corresponding files under `spec-dock/scripts/spec_dock_runtime/`
- Focused tests:
  - `tests/cli_runtime/test_runtime_delete_s13.py`
  - or an existing application delete test if it better isolates metadata cleanup

## Constraints

- Prefer matching existing delete dependency cleanup semantics. If delete already scrubs issue-level references, scrub raw node references in the same transaction shape.
- If raw refs cannot be cleaned safely before destructive work, fail before deleting local files.
- Do not add broad delete refactors.
- Do not resolve GitHub review threads manually.

## Required Regression Shape

Create a source node with a raw dependency on an empty target container, then delete the target recursively:

- raw edge before delete: `init-00001 -> init-00002`
- `init-00002` has no issues
- confirmed recursive delete of `init-00002`

Expected result: after successful delete, `init-00001/.meta.json` no longer contains `init-00002`; alternatively delete fails before local removal with a clear blocking error. The preferred behavior is to follow the existing scrub-on-delete semantics if present.

## Verification

- Run the focused delete regression.
- Run a narrow existing delete suite if the touched code is shared.

## Completion Criteria

- Successful delete cannot leave dangling raw dependency refs to the deleted subtree.
- Existing delete conflict / recursive behavior remains green.
- Changed files and test evidence are reported back to the orchestrator.

## Implementation Result

- Status: implemented
- Changed files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py`
  - `spec-dock/scripts/spec_dock_runtime/application/delete_node.py`
  - `tests/cli_runtime/test_runtime_delete_s13.py`
- Implementation notes:
  - Runtime delete uses `load_node_dependency_resolutions` when available and treats `resolved_node_id in subtree_ids` as the authoritative raw-ref conflict source.
  - Forced delete scrubs the exact `raw_ref` values returned by the resolver, preserving numeric / scoped / URL resolver semantics.
  - Resolver-unavailable fallback preserves direct node-id conflict detection and lets the existing heuristic scrub handle numeric / scoped / URL refs.
- Evidence:
  - Red: direct empty-container raw ref regression failed before implementation because the deleted node id remained in `depends_on`.
  - Red: numeric shorthand empty-container regression failed before follow-up because delete returned `ok` instead of `dependency_conflict`.
  - Red: empty-source raw ref regression failed before follow-up because delete returned `ok` instead of `dependency_conflict`.
  - Red: non-empty-source raw ref regression failed before resolver-based repair because delete returned `ok` instead of `dependency_conflict`.
  - Red: fallback mixed direct+URL regression failed before final fallback repair because URL ref remained in `depends_on`.
  - Green: `uv run pytest tests/cli_runtime/test_runtime_delete_s13.py` -> `53 passed`.
  - Integrated focused bundle after all U003/U004/U005 repairs: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_delete_s13.py` -> `69 passed`.
- Reviewer result: final fresh code-reviewer pass; no findings.
- Re-observation Result: pending push / PR re-observation.
