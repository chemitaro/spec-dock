---
種別: disc
ID: "disc-20260617t041632z-pr-repair-unit-u002"
タイトル: "PR #194 repair unit U002 discussion filenames"
状態: "proposed"
作成者: "codex"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: ["https://github.com/chemitaro/spec-dock/pull/194"]
authority: "proposed"
derived_from: ["20260617t041630z-disc-pr-repair-batch.md"]
reflected_to: []
---

# PR #194 repair unit U002 discussion filenames

## source_batch
- `20260617t041630z-disc-pr-repair-batch.md`

## unit_id
- U002

## covered_ids
- I003

## source_links
- PR review comment 3425508539: discussion draft filenames do not follow catalog naming.

## failure_class
- `review_feedback:discussion-filename`

## risk_class
- minor

## disposition
- fix-now

## Validity Analysis
- Valid. `discussions/rules.md` specifies `<ts>-<kind>-<slug>.md`; delegated design and plan drafts were created with incomplete timestamp and non-catalog kind prefixes.

## Need-To-Fix Decision
- Fix now. The change is low risk and avoids catalog/tooling drift.

## Root Cause
- Delegated draft evidence used ad hoc non-catalog names before final PR review.

## Options Considered
- Leave as grandfathered historical evidence: rejected because this is still current issue evidence in the open PR.
- Rename to catalog-compliant filenames and update references: selected.

## Recommended Design
- Rename:
  - prior design draft -> `20260617t000000z-draft-design-node-level-dependency-mutation.md`
  - prior plan draft -> `20260617t000001z-draft-plan-node-level-dependency-mutation.md`
- Update all references in `requirement.md`, `design.md`, `plan.md`, `report.md`, and discussion front matter / body as needed.

## Implementation Plan
1. Move the two discussion draft files to catalog-compliant names.
2. Update references with repository search.
3. Run `rg` to ensure old filenames are gone.
4. Run `git diff --check` and `./spec-dock/scripts/spec-dock validate`.

## Validation Plan
- The noncompliant-prefix `rg` check for the old design/plan draft names returns no results.
- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`

## Implementation Result
- Renamed design/plan discussion drafts to catalog-compliant filenames.
- Updated references in canonical issue design/plan/report and discussion artifacts.
- Confirmed old draft filename patterns are no longer present under the active issue.

## Commit Evidence
- pending commit

## Re-observation Result
- pending push / re-observation

## Residual Risk / Follow-up
- Low. Local validation passed; PR re-observation remains required.
