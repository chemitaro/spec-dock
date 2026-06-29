---
種別: disc
ID: "20260628t105407z-disc"
タイトル: "PR Repair Unit U001 Plan Readiness"
状態: "implemented"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260628t105407z-disc PR Repair Unit U001 Plan Readiness

## source_batch
- `20260628t105306z-pr-repair-batch`

## unit_id
- U001

## covered_ids
- I001

## source_links
- PR #245 review thread: `PRRT_kwDOQ99OK86Myv-a`
- Review comment: `3487750613`
- File: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`

## failure_class
- `review_feedback:plan-readiness`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- Valid. The current plan readiness classifier can return `executable` when a draft/scaffold plan contains generic template phrases such as `実装ステップ`.
- This directly affects protected `guidance issue-execution` readiness.

## Need-To-Fix Decision
- Fix now. A substantive requirement plus valid assurance must not make issue execution ready until the plan is concrete enough to be executable.

## Root Cause
- `_classify_plan_text` checks positive executable markers before rejecting draft/scaffold metadata and managed placeholder text.

## Options Considered
- Require `状態: approved`: too strict for current dogfooding documents that may still use draft front matter while being explicitly approved elsewhere.
- Reject obvious scaffold/draft/template markers before executable markers: minimal and compatible with current tests.
- Parse full Markdown sections structurally: stronger but larger than this repair unit needs.

## Recommended Design
- Treat front matter `状態: "draft"` / template alternatives and managed placeholder guidance as scaffold before checking executable markers.
- Keep existing substantive executable plan tests passing.

## Implementation Plan
- Update provider and dogfooding runtime `_classify_plan_text`.
- Add focused CLI runtime regression for a draft placeholder plan that contains executable-looking headings.
- Run focused workflow tests.

## Validation Plan
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py`
- Final PR re-observation after all repair units.

## Implementation Result
- Provider and dogfooding runtime `_classify_plan_text` now reject draft/scaffold/template plan markers before checking executable markers.
- Added `test_guidance_blocks_draft_placeholder_plan_even_with_executable_markers` to verify that a draft placeholder plan containing `## 実装ステップ` remains blocked with `plan-not-executable`.

## Commit Evidence
- pending until commit.

## Re-observation Result
- pending after push.

## Residual Risk / Follow-up
- No known residual risk before PR re-observation.

## Validation Result
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/infra/test_init_update.py -k 'issue_244_wait_script_does_not_define_required_check_rollup_reader or issue_232_protected_domain or blocker_policy_no_action or status_rollup_failure_is_ignored or status_rollup_running_is_ignored or draft_placeholder_plan or unknown_root_field'` -> 15 passed.
- `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_assurance_store.py tests/unit/application/test_assurance.py tests/cli_runtime/test_assurance.py` -> 43 passed.
- `uv run pytest tests/unit/infra/test_init_update.py` -> 521 passed.
- `make lint` -> passed.
- `git diff --check` -> passed.
