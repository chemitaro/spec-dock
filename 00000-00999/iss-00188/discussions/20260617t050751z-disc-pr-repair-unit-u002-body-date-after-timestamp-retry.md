---
種別: disc
ID: "20260617t050751z-disc"
タイトル: "PR Repair Unit U002"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
authority: "proposed"
derived_from:
  - "/private/tmp/pr-195-observation-b04c0b1d/result.json"
reflected_to: []
---

# 20260617t050751z-disc PR Repair Unit U002

## Repair Unit Metadata

- source_batch: `20260617t043527z-pr-repair-batch`
- unit_id: U002
- covered_ids: I002
- source_links:
  - `/private/tmp/pr-195-observation-b04c0b1d/result.json`
  - review comment id 3425692862
  - review thread `PRRT_kwDOQ99OK86KGvVm`
- failure_class: `review_feedback:body-date-after-timestamp-retry`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. `plan_discussion_doc` can wait and retry when a timestamp slot is occupied. If that retry crosses UTC midnight, any body/template date calculated before allocation can diverge from the allocated `doc_id` and path.

## Need-To-Fix Decision

Fix now. The generated artifact identity and rendered front matter/body dates should be internally consistent.

## Root Cause

The body replacement context computes `today` before the allocator finalizes the timestamp. The allocator can choose a later timestamp after waiting, but the body renderer still uses the stale pre-allocation date.

## Options Considered

- Recompute the render date from the allocated timestamp after `plan_discussion_doc`; narrowest change and no public interface expansion.
- Return the allocated date from the allocator; larger contract change.
- Ignore the edge case; rejected because the review found a real consistency bug.

## Recommended Design

Derive date placeholders from the actual allocated timestamp / `planned.doc_id` after `plan_discussion_doc` returns. Preserve current timestamp grammar and public command shape.

## Implementation Plan

1. Update provider runtime creation logic in `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` so rendered date placeholders use the allocated timestamp.
2. Mirror any required dogfooding runtime copy if the provider asset contract requires it for local validation.
3. Add or update focused regression coverage for a retry crossing UTC day boundary.
4. Keep changes scoped to body/date consistency; do not change timestamp grammar, sleep policy, or public CLI options.

## Validation Plan

- Run the focused test that covers UTC day rollover after timestamp retry.
- Run relevant new-doc/runtime tests touched by the body renderer.
- Run `git diff --check`.

## Implementation Result

- Implemented by dev-coder `019ed3fd-4373-7000-96f4-c3077d427f2d`.
- Changed provider and dogfooding runtime creation logic:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `spec-dock/scripts/spec_dock_runtime/application/create_node.py`
- Added focused regression:
  - `tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_retry_day_rollover_renders_date_from_allocated_timestamp`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_draft_retry_day_rollover_renders_date_from_allocated_timestamp`
- Red evidence before implementation:
  - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_retry_day_rollover_renders_date_from_allocated_timestamp tests/cli_runtime/test_validate.py::TestCliValidate::test_validate_rejects_malformed_discussion_doc_candidates tests/unit/application/test_validate.py::TestValidateApplication::test_discussion_doc_malformed_candidates_remain_fail_closed` -> 3 failed.
  - U002 failure: rendered `date=2026-03-12` while allocated ID/path used `20260313t000000z...`.
- Green evidence after implementation:
  - same focused command -> 3 passed.
  - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_validate.py tests/unit/application/test_validate.py` -> 67 passed, 6 skipped.
  - QA hardening follow-up: `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py -k draft_retry_day_rollover_renders_date_from_allocated_timestamp` -> 1 passed, 27 deselected.
  - QA hardening follow-up: `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_validate.py tests/unit/application/test_validate.py` -> 68 passed, 6 skipped.
  - `git diff --check` -> pass.
  - `./spec-dock/scripts/spec-dock validate` -> pass, `nodes=97`.

## Commit Evidence

- pending repair commit

## Re-observation Result

- pending PR re-observation after repair commit/push

## Residual Risk / Follow-up

- No known residual risk after focused, related, and draft-path hardening verification; PR re-observation still required to close thread `PRRT_kwDOQ99OK86KGvVm`.
