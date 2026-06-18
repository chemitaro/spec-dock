---
種別: disc
ID: "20260618t202851z-disc"
タイトル: "PR Repair Unit U002"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00207"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260618t202851z-disc PR Repair Unit U002

## source_batch

- `20260618t194321z-pr-repair-batch`

## unit_id

- U002

## covered_ids

- I003: Read cached node kind from the generated field
- I004: Reuse cached high-level state during offline sync
- I005: Reuse cached high-level state for offline active set

## source_links

- PR: https://github.com/chemitaro/spec-dock/pull/208
- Observation head SHA: `b506e0abcc8749bc679d28c78f71efcfa170fb9b`
- I003 thread: `PRRT_kwDOQ99OK86Kqu-H`
- I004 thread: `PRRT_kwDOQ99OK86Kqu-M`
- I005 thread: `PRRT_kwDOQ99OK86Kqu-P`

## failure_class

- `review_feedback:cached-node-kind-schema`
- `review_feedback:offline-sync-cache`
- `review_feedback:offline-active-set-cache`

## risk_class

- blocking

## disposition

- fix-now

## Validity Analysis

All findings are valid. The generated `.agent/index*.json` node payload uses `type`, so a cache reader that checks only `kind` misses real high-level nodes. Offline `sync` and `active set` also need the same cached high-level state to avoid converting a previously closed empty high-level dependency into an unknown node blocker.

## Need-To-Fix Decision

Fix now. These are direct continuations of the cached high-level dependency readiness contract introduced for this issue.

## Root Cause

The first cached-state repair was local to `deps check --no-github`, did not match the generated artifact schema, and was not propagated into the other offline readiness callers.

## Options Considered

- Only update the unit test to use `type`: rejected because offline sync and active-set paths would still regress.
- Add separate one-off readers in each caller: rejected to avoid duplicated schema handling.
- Share cached high-level state loading and pass the result into check/sync/active readiness evaluation: selected.

## Recommended Design

- Make cached high-level state loading understand generated `type` and tolerate legacy `kind` only as compatibility.
- Reuse the cached high-level state in offline `check_deps`, `sync_state`, and `set_active`.
- Add focused regressions for generated schema, offline sync, and offline active set.

## Implementation Plan

1. Add or update tests so generated `type` is used in cached artifacts.
2. Update cached high-level state reader and propagate it through `sync_state` and `set_active`.
3. Mirror provider runtime changes into dogfooding runtime files.
4. Run focused tests, `git diff --check`, `validate`, and broad unit / CLI runtime tests.

## Validation Plan

- Focused unit / CLI tests for I003, I004, and I005.
- `git diff --check`
- `./spec-dock/scripts/spec-dock validate`
- `uv run pytest tests/unit tests/cli_runtime`

## Implementation Result

- Implemented.
- Cached high-level state loading now reads generated `type` and tolerates legacy `kind`.
- Offline `check_deps`, `sync_state`, and `set_active` pass cached high-level `github.state` into high-level readiness resolution.
- Added / updated regressions for generated schema, offline sync, and offline active-set reuse.
- Provider runtime changes were mirrored into `spec-dock/scripts/spec_dock_runtime/...`.

## Commit Evidence

- pending commit after parent integration.
- Parent verification before commit:
  - `uv run pytest tests/unit/application/test_check_deps.py::TestCheckDepsApplication::test_no_github_uses_cached_high_level_github_state_from_sync_artifact tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_no_github_uses_cached_high_level_github_state tests/cli_runtime/test_sync.py::TestCliSync::test_sync_deps_issues_marks_empty_closed_epic_dependency_satisfied` -> 3 passed
  - `git diff --check` -> pass
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=130`
  - `uv run pytest tests/unit tests/cli_runtime` -> 1329 passed, 76 skipped

## Re-observation Result

- pending

## Residual Risk / Follow-up

- pending re-observation
