---
種別: disc
ID: "20260618t194411z-disc"
タイトル: "PR Repair Unit U001"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00207"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260618t194411z-disc PR Repair Unit U001

## source_batch

- `20260618t194321z-pr-repair-batch`

## unit_id

- U001

## covered_ids

- I001: Skip node blockers for completed source issues
- I002: Preserve cached high-level GitHub states

## source_links

- PR: https://github.com/chemitaro/spec-dock/pull/208
- Observation head SHA: `8ca6cd6e1c7a9899b20b69445c61343e2b455633`
- I001 thread: `PRRT_kwDOQ99OK86KqG36`
- I002 thread: `PRRT_kwDOQ99OK86KqG3_`

## failure_class

- `review_feedback:completed-source-node-blocker`
- `review_feedback:cached-high-level-state`

## risk_class

- blocking

## disposition

- fix-now

## Validity Analysis

Both review findings are valid.

I001 shows that a completed source issue can be marked blocked again when its raw high-level dependency context points to an open or unknown empty initiative/epic. Completed issues should remain ready and should not receive new node blockers.

I002 shows that no-github cached high-level status resolution reads `nodes[*].status`, while sync artifacts store initiative/epic GitHub state under `github.state`. A previously synced closed high-level dependency can therefore become unknown in cached mode.

## Need-To-Fix Decision

Fix both findings before the PR is merge-prepared. They are within the issue scope because the issue is specifically about high-level dependency readiness projection and rendering correctness.

## Root Cause

- Node blocker evaluation is applied even when the source issue is already done/closed.
- Cached high-level status resolution does not read the high-level node GitHub state shape written by sync artifacts.

## Options Considered

- No action: rejected because both findings describe observable readiness regressions.
- Follow-up issue: rejected because both fixes are small, local, and within the current issue scope.
- Fix now with focused regressions: selected.

## Recommended Design

- In domain readiness evaluation, treat completed source issues as ready and skip adding node blockers for their high-level dependency contexts.
- In cached high-level status resolution, read high-level GitHub state from cached artifact fields compatible with sync output, especially `github.state`.
- Add regressions for:
  - done source issue with open/unknown empty high-level dependency remains ready;
  - no-github cached closed high-level dependency remains satisfied.

## Implementation Plan

1. Add focused failing tests for I001 and I002 using existing domain / CLI runtime patterns.
2. Update provider runtime in the correct layer:
   - `domain/deps.py` for completed source node blocker behavior.
   - `application/check_deps.py` for cached high-level GitHub state resolution.
3. Mirror changed provider runtime files into `spec-dock/scripts/spec_dock_runtime/...`.
4. Run focused tests, `git diff --check`, `validate`, and broad `tests/unit tests/cli_runtime` if feasible.
5. Commit and push the repair, then re-observe PR #208 latest head SHA.

## Validation Plan

- Focused tests for I001 and I002.
- Existing dependency tests around empty open/closed high-level contexts.
- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`
- `uv run pytest tests/unit tests/cli_runtime`

## Implementation Result

- Implemented.
- `domain/deps.py` now skips high-level node blocker evaluation for source issues whose effective issue status is `done`.
- `application/check_deps.py` now reads cached high-level GitHub state from `.agent/index-all.json` / `.agent/index.json` `nodes[*].github.state` for `--no-github` flows.
- Added focused regressions:
  - `tests/unit/domain/test_deps.py::TestDepsDomain::test_evaluate_readiness_does_not_apply_node_blockers_to_done_source_issue`
  - `tests/unit/application/test_check_deps.py::TestCheckDepsApplication::test_no_github_uses_cached_high_level_github_state_from_sync_artifact`
- Provider runtime changes were mirrored into `spec-dock/scripts/spec_dock_runtime/...`.

## Commit Evidence

- pending commit after parent integration.
- Parent verification before commit:
  - `uv run pytest tests/unit/domain/test_deps.py::TestDepsDomain::test_evaluate_readiness_does_not_apply_node_blockers_to_done_source_issue tests/unit/application/test_check_deps.py::TestCheckDepsApplication::test_no_github_uses_cached_high_level_github_state_from_sync_artifact` -> 2 passed
  - `git diff --check` -> pass
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=130`
  - `uv run pytest tests/unit tests/cli_runtime` -> 1328 passed, 76 skipped

## Re-observation Result

- pending

## Residual Risk / Follow-up

- pending re-observation
