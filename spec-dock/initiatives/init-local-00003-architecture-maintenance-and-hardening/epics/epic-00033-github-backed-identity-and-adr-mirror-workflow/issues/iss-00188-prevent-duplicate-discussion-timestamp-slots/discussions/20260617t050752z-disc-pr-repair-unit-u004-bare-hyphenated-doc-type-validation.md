---
種別: disc
ID: "20260617t050752z-disc"
タイトル: "PR Repair Unit U004"
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

# 20260617t050752z-disc PR Repair Unit U004

## Repair Unit Metadata

- source_batch: `20260617t043527z-pr-repair-batch`
- unit_id: U004
- covered_ids: I004
- source_links:
  - `/private/tmp/pr-195-observation-b04c0b1d/result.json`
  - review comment id 3425692872
  - review thread `PRRT_kwDOQ99OK86KGvVr`
- failure_class: `review_feedback:bare-hyphenated-doc-type-validation`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. `pr-repair-batch.md` in a `discussions/` directory expresses an obvious manual/malformed intent for the new doc type, but current malformed-intent detection only catches prefixed stems followed by `-` or `_`.

## Need-To-Fix Decision

Fix now. #188's fail-closed validation contract should catch malformed manual `pr-repair-batch` artifacts rather than silently ignoring them.

## Root Cause

The parser catalog added a hyphenated doc type but did not expand malformed-intent detection to exact known doc-type stems.

## Options Considered

- Reject exact bare stems for all known discussion doc types.
- Reject exact bare stems only for hyphenated doc types.
- Leave exact stems ignored.

## Recommended Design

Reject exact bare known doc-type filenames in `discussions/` validation, with focused tests for `pr-repair-batch.md`. Preserve all valid timestamped filenames.

## Implementation Plan

1. Update provider runtime parser/validation logic in `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py`.
2. Mirror the dogfooding runtime copy if required by asset parity.
3. Add a validation regression test for exact bare `pr-repair-batch.md`.
4. Keep valid `20260617t000000z-pr-repair-batch-title.md` behavior unchanged.

## Validation Plan

- Run focused validation tests covering valid and malformed `pr-repair-batch`.
- Run relevant new-doc validation tests.
- Run `git diff --check`.

## Implementation Result

- Implemented by dev-coder `019ed3fd-4373-7000-96f4-c3077d427f2d`.
- Changed provider and dogfooding runtime validation logic:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py`
  - `spec-dock/scripts/spec_dock_runtime/domain/discussion_docs.py`
- Added validation regressions:
  - `tests/cli_runtime/test_validate.py`
  - `tests/unit/application/test_validate.py`
- Red evidence before implementation:
  - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_retry_day_rollover_renders_date_from_allocated_timestamp tests/cli_runtime/test_validate.py::TestCliValidate::test_validate_rejects_malformed_discussion_doc_candidates tests/unit/application/test_validate.py::TestValidateApplication::test_discussion_doc_malformed_candidates_remain_fail_closed` -> 3 failed.
  - U004 failure: `pr-repair-batch.md` passed validation.
- Green evidence after implementation:
  - same focused command -> 3 passed.
  - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_validate.py tests/unit/application/test_validate.py` -> 67 passed, 6 skipped.
  - `git diff --check` -> pass.
  - `./spec-dock/scripts/spec-dock validate` -> pass, `nodes=97`.

## Commit Evidence

- pending repair commit

## Re-observation Result

- pending PR re-observation after repair commit/push

## Residual Risk / Follow-up

- No known residual risk after focused and related verification; PR re-observation still required to close thread `PRRT_kwDOQ99OK86KGvVr`.
