---
種別: disc
ID: "20260618t221656z-disc"
タイトル: "PR Repair Unit U004"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00207"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260618t221656z-disc PR Repair Unit U004

## source_batch

- `20260618t194321z-pr-repair-batch`

## unit_id

- U004

## covered_ids

- I007: Preserve cached high-level GitHub state across repeated `sync --no-github`
- I008: Preserve all-done expanded high-level dependencies as satisfied

## source_links

- PR: https://github.com/chemitaro/spec-dock/pull/208
- Observation head SHA: `9be1681c3d05b3434255ef87cfcba64d6b28bfa0`
- I007 thread: `PRRT_kwDOQ99OK86KrvkL`
- I007 comment: `3439052488`
- I008 thread: `PRRT_kwDOQ99OK86KrvkQ`
- I008 comment: `3439052493`

## failure_class

- `review_feedback:offline-high-level-cache-erasure`
- `review_feedback:expanded-all-done-satisfied-dependency`

## risk_class

- blocking

## disposition

- fix-now

## Validity Analysis

Both findings are valid.

I007 showed that `sync --no-github` could consume cached high-level GitHub state for the current run, then rewrite `.agent/index-all.json` without preserving that high-level `github.state`. A second offline sync or `deps check --no-github` could therefore lose the closed/open high-level state and regress to `empty_unknown`.

I008 showed that expanded high-level dependency contexts with all child issues `done` were not recorded as satisfied when the parent initiative / epic remained open. Readiness was true through compiled issue dependencies, but the raw high-level edge disappeared from `deps-issues` instead of being shown as satisfied.

## Need-To-Fix Decision

Fix now. Both findings affect dependency projection accuracy and the user-facing `deps-issues` / `deps check` readiness explanation.

## Root Cause

- I007: index rendering did not re-emit high-level cached GitHub state when the sync result came from cache rather than live GitHub snapshots.
- I008: dependency context satisfaction checked only the high-level node state and did not consider `target_issue_ids` all done for expanded contexts.

## Options Considered

- Leave as residual review threads: rejected because both are in-scope correctness gaps.
- Preserve cache in a new sidecar file: rejected because current offline readers already use `.agent/index-all.json` / `.agent/index.json`.
- Re-emit cached high-level state into existing index payloads and treat all-done expanded contexts as satisfied: selected.

## Recommended Design

- When rendering sync index payloads, preserve initiative / epic `github.state` and a freshness marker for high-level status contexts whose source is `github` or `cache`.
- In domain dependency context evaluation, record a high-level context as satisfied when all `target_issue_ids` are `done`, even if the parent high-level node is still open.
- Keep empty unknown behavior unchanged for high-level dependencies without known state or done child issues.

## Implementation Result

- Implemented.
- `presentation/json_state.py` now re-emits high-level `github.state` for `github` / `cache` high-level visual states during sync output rendering.
- `domain/deps.py` now records expanded contexts with all target issues `done` as satisfied dependencies.
- Added / updated regressions:
  - repeated `sync --no-github` preserves empty closed epic satisfied dependency and `deps check --no-github` remains ready;
  - all-done expanded high-level dependency is emitted as a satisfied edge in `deps-issues`;
  - domain readiness records all-done expanded high-level context as satisfied.
- Provider runtime changes were mirrored into `spec-dock/scripts/spec_dock_runtime/...`.

## Commit Evidence

- pending commit after parent integration.
- Parent verification before commit:
  - `uv run pytest tests/unit/domain/test_deps.py::TestDepsDomain::test_evaluate_readiness_records_expanded_all_done_high_level_dependency_as_satisfied -q` -> 1 passed
  - `uv run pytest tests/cli_runtime/test_sync.py::TestCliSync::test_sync_deps_issues_marks_empty_closed_epic_dependency_satisfied tests/cli_runtime/test_sync.py::TestCliSync::test_sync_deps_issues_records_all_done_expanded_high_level_dependency_as_satisfied -q` -> 2 passed
  - `uv run pytest tests/unit/domain/test_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_sync.py` -> 97 passed, 2 skipped
  - `uv run pytest tests/unit tests/cli_runtime` -> 1332 passed, 76 skipped
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=130`
  - `git diff --check` -> pass
  - provider / dogfooding mirror `diff -u` for changed runtime files -> no diff

## Step Review

- `code-reviewer` `review_status=pass`; no findings.

## Re-observation Result

- pending after commit and push.

## Residual Risk / Follow-up

- pending re-observation.

## Ledger Note

- No material implementation decisions beyond the approved plan.
- Risk note: offline-preserved high-level cache uses sync `generated_at` as cache freshness marker, not as evidence of a new GitHub fetch.
