---
種別: disc
ID: "20260628t114108z-disc"
タイトル: "PR Repair Unit U004 Provider CI Rollup Tests"
状態: "implemented"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260628t114108z-disc PR Repair Unit U004 Provider CI Rollup Tests

## source_batch
- `20260628t105306z-pr-repair-batch`

## unit_id
- U004

## covered_ids
- I006

## source_links
- PR #245 observation result: `/private/tmp/spec-dock-iss-00244-pr245-observation-621b59b3/result.json`
- GitHub Actions run: `Provider CI` run `28320468406`
- Failed job: `provider-tests` job `83901426510`
- Failed tests:
  - `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_keeps_required_checks_pending_as_wait`
  - `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_244_pr_observation_wait_ignores_failed_required_rollup`
  - `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_244_pr_observation_wait_ignores_failed_required_status_state`

## failure_class
- `check_failure:Provider CI/provider-tests`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- Valid. The PR observation re-run for head `621b59b3906983a5b3bb3221a73f0615e67d39e7` failed because Provider CI still contained tests expecting `timeout` when the fake scenario had Actions CI passed and review approved.
- After U002, `mergeStateStatus` and `statusCheckRollup` are intentionally ignored. Therefore these scenarios should become `passed` / `merge_prepared`, not wait for missing rollup state.
- The old expectation was timing-sensitive: it could pass locally by timing out before the completion gate, but fail on CI when the script reached completion first.

## Need-To-Fix Decision
- Fix now. This is the only observed CI blocker after U001-U003 and prevents the PR from becoming merge-prepared.

## Root Cause
- The test assertions were only partially updated after removing the PR rollup decision path. They still encoded the old "wait because rollup is pending/failed" expectation.
- Short `--timeout-seconds 2` values made the tests depend on runtime timing instead of the intended contract.

## Options Considered
- Keep `timeout` expected: rejected because it contradicts the new Actions-only contract.
- Remove the tests: rejected because they still protect the regression that rollup state must not block merge-prepared.
- Update expected status to `passed` and increase test timeout budget: chosen because it verifies the new contract without timing flakiness.

## Recommended Design
- For fake scenarios with `ci: passed` and `review: approved`, assert `normalized_status == "passed"`, `recommended_next_action == "merge_prepared"`, and `observation_complete is True`, even when `merge_state_status` is blocked or `status_check_rollup` is pending/failed.
- Increase the test process budget for these scenarios so they can reach the stable completion path deterministically.

## Implementation Plan
- Update the three affected test expectations in `tests/unit/infra/test_init_update.py`.
- Keep the test scenarios' `merge_state_status` and `status_check_rollup` fields present to prove they are ignored.
- Re-run the affected tests, full `test_init_update.py`, lint, and diff check.

## Implementation Result
- Updated the three rollup-related wait tests to expect `passed` / `merge_prepared`.
- Increased their timeout budgets to avoid local/CI timing dependence.

## Commit Evidence
- pending until amend commit.

## Re-observation Result
- pending after push and PR re-observation for the amended head.

## Residual Risk / Follow-up
- No known residual risk. If Provider CI still fails after re-observation, treat the new failure as a separate repair item.

## Validation Result
- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_keeps_required_checks_pending_as_wait tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_244_pr_observation_wait_ignores_failed_required_rollup tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_244_pr_observation_wait_ignores_failed_required_status_state` -> 3 passed.
- `uv run pytest tests/unit/infra/test_init_update.py` -> 521 passed.
- `make lint` -> passed.
- `git diff --check` -> passed.
