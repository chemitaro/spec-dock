---
種別: disc
ID: "20260628t105406z-disc"
タイトル: "PR Repair Unit U002 PR Observation Decision"
状態: "implemented"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260628t105406z-disc PR Repair Unit U002 PR Observation Decision

## source_batch
- `20260628t105306z-pr-repair-batch`

## unit_id
- U002

## covered_ids
- I002, I003, I004

## source_links
- PR #245 review threads: `PRRT_kwDOQ99OK86Myv-b`, `PRRT_kwDOQ99OK86Myv-c`, `PRRT_kwDOQ99OK86Myv-d`
- Review comments: `3487750614`, `3487750615`, `3487750616`
- Files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`

## failure_class
- `review_feedback:pr-observation-decision`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- Valid. The wait script currently queries PR rollup data even though the adjacent skill contract forbids Checks/status rollup surfaces as CI evidence.
- Valid. `blocker_policy_no_action` is a positive completion signal but is not treated as explicit completion by the no-completion evidence logic.
- Valid. Protected-domain detection omits the repository protected domains now encoded in the review instruction.

## Need-To-Fix Decision
- Fix now. These paths directly affect PR observation and merge-prepared semantics.

## Root Cause
- PR observation implementation drifted from the Actions-only and blocker-centric review contract.

## Options Considered
- Keep rollup query as a merge blocker fallback: rejected because the skill explicitly forbids rollup/check surfaces as CI evidence.
- Remove rollup query/override and rely on Actions collector plus explicit external residual risk: chosen.
- Keep protected-domain list small: rejected because this repository's protected domains are workflow/review/schema/dependency oriented.

## Recommended Design
- Remove `required_check_rollup_status` and all decision overrides based on `mergeStateStatus,statusCheckRollup`.
- Add `blocker_policy_no_action` to explicit completion / no-completion exclusion semantics.
- Expand protected-domain patterns to include PR observation, merge-prepared, CI/review gates, guidance/execution-ready, assurance/schema, dependency/sync/active, destructive operations, symlink/path traversal, install/update/migration, and provider/dogfooding parity.

## Implementation Plan
- Patch provider and dogfooding copies of `pr_observation_wait.py` and `pr_review_snapshot.py`.
- Update/remove tests that expected `statusCheckRollup` use.
- Add regression tests for no rollup calls, blocker-policy no-action completion, and protected-domain promotion.

## Validation Plan
- Focused PR observation tests under `tests/unit/infra/test_init_update.py`.
- `make lint`.
- Final PR re-observation after push.

## Implementation Result
- Removed `required_check_rollup_status` and the `mergeStateStatus,statusCheckRollup` decision override from the PR observation wait path.
- Added `blocker_policy_no_action` as explicit review completion evidence.
- Expanded protected-domain matching to cover PR observation, merge-prepared, CI/review gates, guidance/execution-ready, assurance/schema, dependency/sync, destructive operations, symlink/path traversal, install/update, shipped assets, and provider/dogfooding parity.
- Updated regression coverage to assert no PR rollup query remains and that protected domains / blocker-policy completion are recognized.

## Commit Evidence
- pending until commit.

## Re-observation Result
- pending after push.

## Residual Risk / Follow-up
- External/non-Actions checks remain intentionally unobserved by PR observation and must be treated as residual risk or human/GitHub UI confirmation, not as script-observed pass.

## Validation Result
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/infra/test_init_update.py -k 'issue_244_wait_script_does_not_define_required_check_rollup_reader or issue_232_protected_domain or blocker_policy_no_action or status_rollup_failure_is_ignored or status_rollup_running_is_ignored or draft_placeholder_plan or unknown_root_field'` -> 15 passed.
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/application/test_assurance.py tests/cli_runtime/test_assurance.py` -> 43 passed.
- `uv run pytest tests/unit/infra/test_init_update.py` -> 521 passed.
- `make lint` -> passed.
- `git diff --check` -> passed.
