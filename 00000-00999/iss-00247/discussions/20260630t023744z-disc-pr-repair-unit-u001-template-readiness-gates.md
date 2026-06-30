---
種別: disc
ID: "20260630t023744z-disc"
タイトル: "PR Repair Unit U001"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["iss-00247"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260630t023744z-disc PR Repair Unit U001

## Repair Unit Contract

- source_batch: `20260630t023709z-pr-repair-batch`
- unit_id: U001
- covered_ids: I001, I002, I003, I004, I005
- source_links:
  - https://github.com/chemitaro/spec-dock/pull/248#discussion_r3495817493
  - https://github.com/chemitaro/spec-dock/pull/248#discussion_r3495817497
  - https://github.com/chemitaro/spec-dock/pull/248#discussion_r3495817499
  - https://github.com/chemitaro/spec-dock/pull/248#discussion_r3495980801
  - https://github.com/chemitaro/spec-dock/pull/248#discussion_r3496085594
- failure_class: `review_feedback:template-readiness`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

The findings are valid. The PR adds `XXX` sentinel rows, generated `M...` milestone IDs, and milestone-level `commit候補` gates, but the runtime readiness checks and workflow completion wording still contained older assumptions that could allow partially generated artifacts to appear executable.

## Need-To-Fix Decision

Fix now. The affected surfaces are issue readiness and completion gates, which are protected domains for this PR.

## Root Cause

Template authoring guidance moved ahead of readiness and completion enforcement. Generated sentinel tokens, unhyphenated milestone placeholder IDs, report evidence anchors, and single placeholder cells/list fields were not fully represented in runtime scaffold detection, and workflow completion text still implied mandatory per-step commit closure.

## Options Considered

- Documentation-only waiver: rejected because readiness false positives would remain.
- Remove `XXX` sentinels from templates: rejected because they intentionally communicate arbitrary extension rows.
- Align readiness detection and workflow wording: selected because it preserves the template design and blocks unsafe execution handoff.

## Recommended Design

- Treat remaining generated placeholder table cells and list items as scaffold markers even when only one placeholder remains.
- Treat unhyphenated generated placeholder IDs such as `M...` as scaffold markers.
- Treat generated `report.md#...` evidence anchors as scaffold markers.
- Treat requirement sentinels `SC-XXX`, `BH-XXX`, `AC-XXX`, `B-CAND-XXX`, and `TERM-XXX` as scaffold markers.
- Update workflow completion wording from per-step commit closure to step / milestone result approval with milestone `commit候補` gates for standard and above.

## Implementation Plan

- Add regression tests for requirement sentinel detection and single placeholder plan readiness.
- Update provider and dogfooding runtime readiness helpers.
- Update provider and dogfooding workflow / issue-plan docs.
- Run focused tests, lint, and full pytest before pushing.

## Validation Plan

- `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py -k "sentinel or single_generated or placeholder_list"`
- `uv run pytest tests/unit/infra/test_init_update.py -k "issue_102_agentic_tdd_contract_assets or issue_247_grade_profile_template_followup_contract_assets or spec_document_templates_keep_policy_out_of_scaffold"`
- `make lint`
- `uv run pytest`

## Implementation Result

- Added requirement sentinel scaffold detection for `SC-XXX`, `BH-XXX`, `AC-XXX`, `B-CAND-XXX`, and `TERM-XXX`.
- Updated plan/design readiness placeholder detection so single generated placeholder table cells and generated placeholder list items keep the artifact non-executable.
- Aligned workflow completion docs from per-step commit wording to step / milestone result approval with milestone `commit候補` gates for standard and above.
- Added regression coverage for requirement sentinels, single placeholder table cells, placeholder list fields, report anchor placeholders, and unhyphenated milestone placeholder IDs.

## Commit Evidence

- Repair commit: this repair unit is included in the amended commit `fix(workflow): テンプレート残存placeholderのready誤判定を防止`.
- Final pushed SHA is recorded by PR metadata and re-observation evidence after push.

## Re-observation Result

pending re-observation after push

## Residual Risk / Follow-up

No known local residual risk after `make lint` and full `uv run pytest`; latest-head PR re-observation is still required.
