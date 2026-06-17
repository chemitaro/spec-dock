---
種別: disc
ID: "20260617t055226z-disc"
タイトル: "PR Repair Unit U007"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
authority: "proposed"
derived_from:
  - "/private/tmp/pr-195-observation-bb0b751a/result.json"
reflected_to: []
---

# 20260617t055226z-disc-disc PR Repair Unit U007

## Repair Unit Metadata

- source_batch: `20260617t043527z-pr-repair-batch`
- unit_id: U007
- covered_ids: I007
- source_links:
  - `/private/tmp/pr-195-observation-bb0b751a/result.json`
  - review comment id 3425870063
  - review thread `PRRT_kwDOQ99OK86KHORP`
- failure_class: `review_feedback:suffix-fallback-original-timestamp`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. The latest PR observation selected this finding in the current trigger boundary for commit `bb0b751a58b7d86f9f01feff89e5d0e2c2333bfa`, and the concern maps to a shipped surface changed or affected by #188.

## Need-To-Fix Decision

Fix now. Leaving this unresolved would keep the current PR review thread open and would either break a generated-artifact workflow or leave shipped user-facing docs stale.

## Root Cause

suffix fallback may switch to later occupied timestamp family.

## Options Considered

- Defer as follow-up and stop at a human gate.
- Repair now with the smallest scoped change and focused verification.

## Recommended Design

Preserve the original colliding timestamp family for suffix fallback while still allowing a later free standard timestamp slot to win. Add regression coverage where a later timestamp is occupied/exhausted but the original family has suffix capacity.

## Implementation Plan

1. Inspect the affected provider-side source/docs and the dogfooding mirror or tests that cover it.
2. Apply the smallest provider-side correction and mirror generated/dogfooding copies only where repository parity requires it.
3. Add or update focused regression/inspection coverage for this repair unit.
4. Avoid public CLI interface changes, timestamp grammar changes outside U007 behavior, and any new `pr-repair-unit` doc type.

## Validation Plan

Run focused timestamp allocator tests, relevant new-doc runtime tests, and `git diff --check`.

## Implementation Result

- Implemented by dev-coder `019ed425-038e-7bd3-b819-7c7a33ca1c5f`.
- Changed provider and dogfooding timestamp allocator:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `spec-dock/scripts/spec_dock_runtime/application/create_node.py`
- Added focused regression:
  - `tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_later_occupied_timestamp_exhaustion_falls_back_to_original_family`
- Red / characterization:
  - Added regression initially failed with later family `20260312t010204z` suffix exhaustion.
- Green evidence:
  - focused U007 test -> 1 passed.
  - `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_new.py tests/cli_runtime/test_validate.py` -> 103 passed, 11 skipped.
  - provider/dogfooding `create_node.py` diff -> no output.
  - `git diff --check` -> pass.

## Commit Evidence

- pending repair commit

## Re-observation Result

- pending PR re-observation after repair commit/push

## Residual Risk / Follow-up

- No known residual risk after focused allocator and related new-doc verification; PR re-observation still required to close thread `PRRT_kwDOQ99OK86KHORP`.
