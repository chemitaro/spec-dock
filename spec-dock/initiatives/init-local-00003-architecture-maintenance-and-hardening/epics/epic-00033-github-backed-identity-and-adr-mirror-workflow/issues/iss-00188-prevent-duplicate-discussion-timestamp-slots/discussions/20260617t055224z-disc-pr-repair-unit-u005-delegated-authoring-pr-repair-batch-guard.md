---
種別: disc
ID: "20260617t055224z-disc"
タイトル: "PR Repair Unit U005"
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

# 20260617t055224z-disc-disc PR Repair Unit U005

## Repair Unit Metadata

- source_batch: `20260617t043527z-pr-repair-batch`
- unit_id: U005
- covered_ids: I005
- source_links:
  - `/private/tmp/pr-195-observation-bb0b751a/result.json`
  - review comment id 3425870058
  - review thread `PRRT_kwDOQ99OK86KHORK`
- failure_class: `review_feedback:delegated-diff-guard-pr-repair-batch`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. The latest PR observation selected this finding in the current trigger boundary for commit `bb0b751a58b7d86f9f01feff89e5d0e2c2333bfa`, and the concern maps to a shipped surface changed or affected by #188.

## Need-To-Fix Decision

Fix now. Leaving this unresolved would keep the current PR review thread open and would either break a generated-artifact workflow or leave shipped user-facing docs stale.

## Root Cause

delegated diff guard rejects generated pr-repair-batch docs.

## Options Considered

- Defer as follow-up and stop at a human gate.
- Repair now with the smallest scoped change and focused verification.

## Recommended Design

Update delegated authoring diff guard so runtime-generated `pr-repair-batch` discussion filenames are accepted. Prefer reusing shared parser/catalog or add the new type to the guard with focused regression coverage.

## Implementation Plan

1. Inspect the affected provider-side source/docs and the dogfooding mirror or tests that cover it.
2. Apply the smallest provider-side correction and mirror generated/dogfooding copies only where repository parity requires it.
3. Add or update focused regression/inspection coverage for this repair unit.
4. Avoid public CLI interface changes, timestamp grammar changes outside U007 behavior, and any new `pr-repair-unit` doc type.

## Validation Plan

Run focused delegated authoring diff-guard tests, relevant validation/new-doc tests, and `git diff --check`.

## Implementation Result

- Implemented by dev-coder `019ed425-038e-7bd3-b819-7c7a33ca1c5f`.
- Changed provider and dogfooding runtime diff guard:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `spec-dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
- Added focused regression:
  - `tests/unit/domain/test_delegated_authoring.py::TestDelegatedAuthoringRuntimeDomain::test_diff_guard_allows_new_pr_repair_batch_discussion_markdown`
- Red / characterization:
  - Added regression initially failed with `discussion_name_noncompliant` / `expected_exactly_one_new_discussion_draft count=0`.
- Green evidence:
  - focused U005 test -> 1 passed.
  - code-review follow-up red: real runtime-generated `pr-repair-batch` template regression failed with `new_discussion_missing_proposed_state`.
  - code-review / QA follow-up green: `uv run pytest tests/unit/domain/test_delegated_authoring.py -k 'runtime_generated_pr_repair_batch_template or new_pr_repair_batch_discussion_markdown or mismatched_generated_id or mismatched_scope'` -> 5 passed, 22 deselected.
  - QA follow-up: `test_diff_guard_rejects_pr_repair_batch_template_with_mismatched_scope` added for the generated `親` mismatch guard.
  - `uv run pytest tests/unit/domain/test_delegated_authoring.py tests/cli_runtime/test_delegated_authoring.py` -> 45 passed, 31 skipped.
  - provider/dogfooding `delegated_authoring.py` diff -> no output.
  - `git diff --check` -> pass.

## Commit Evidence

- pending repair commit

## Re-observation Result

- pending PR re-observation after repair commit/push

## Residual Risk / Follow-up

- No known residual risk after focused diff-guard, generated-template, ID mismatch rejection, scope mismatch rejection, and parity verification; PR re-observation still required to close thread `PRRT_kwDOQ99OK86KHORK`.
