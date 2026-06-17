---
種別: disc
ID: "20260617t055225z-disc"
タイトル: "PR Repair Unit U006"
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

# 20260617t055225z-disc-disc PR Repair Unit U006

## Repair Unit Metadata

- source_batch: `20260617t043527z-pr-repair-batch`
- unit_id: U006
- covered_ids: I006
- source_links:
  - `/private/tmp/pr-195-observation-bb0b751a/result.json`
  - review comment id 3425870061
  - review thread `PRRT_kwDOQ99OK86KHORN`
- failure_class: `review_feedback:shipped-readme-pr-repair-batch-catalog`
- risk_class: material-follow-up
- disposition: fix-now

## Validity Analysis

Valid. The latest PR observation selected this finding in the current trigger boundary for commit `bb0b751a58b7d86f9f01feff89e5d0e2c2333bfa`, and the concern maps to a shipped surface changed or affected by #188.

## Need-To-Fix Decision

Fix now. Leaving this unresolved would keep the current PR review thread open and would either break a generated-artifact workflow or leave shipped user-facing docs stale.

## Root Cause

shipped README catalog omits pr-repair-batch.

## Options Considered

- Defer as follow-up and stop at a human gate.
- Repair now with the smallest scoped change and focused verification.

## Recommended Design

Update shipped README catalog surfaces so installed docs mention `pr-repair-batch` as a supported `new doc` discussion type/path. Keep this as catalog parity only.

## Implementation Plan

1. Inspect the affected provider-side source/docs and the dogfooding mirror or tests that cover it.
2. Apply the smallest provider-side correction and mirror generated/dogfooding copies only where repository parity requires it.
3. Add or update focused regression/inspection coverage for this repair unit.
4. Avoid public CLI interface changes, timestamp grammar changes outside U007 behavior, and any new `pr-repair-unit` doc type.

## Validation Plan

Run targeted README/catalog inspections, relevant asset parity tests, and `git diff --check`.

## Implementation Result

- Implemented by doc-writer `019ed425-30f8-79f1-8c6d-cbb260b3f610`.
- Changed provider and dogfooding shipped README surfaces:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/scripts/README.md`
  - `spec-dock/templates/README.md`
  - `spec-dock/scripts/README.md`
- Added `pr-repair-batch` to shipped discussion catalog references and `new doc pr-repair-batch` examples.
- Verification:
  - targeted `rg -n "pr-repair-batch" ...README.md` found provider and mirror README entries.
  - provider/dogfooding README comparisons -> pass.
  - QA follow-up: `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_188_pr_repair_batch_readme_catalog_assets'` -> 1 passed.
  - `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set tests/unit/infra/test_init_update.py::TestInitUpdate::test_current_guidance_documents_match_discussion_numbering_contract` -> 3 passed.
  - `git diff --check` -> pass.

## Commit Evidence

- pending repair commit

## Re-observation Result

- pending PR re-observation after repair commit/push

## Residual Risk / Follow-up

- No known residual risk after catalog inspection, README pin test, and asset guidance tests; PR re-observation still required to close thread `PRRT_kwDOQ99OK86KHORN`.
