---
種別: disc
ID: "20260702t020503z-03-disc"
タイトル: "Phase 3 Quality Delivery Gate Model"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t015343z-interview"
  - "20260702t014409z-research"
authority: "proposed"
derived_from:
  - "V3 issues/issue-06-epic-quality-gate-manual-tests-and-pr-delivery.md"
  - "V3 reference/quality-gate-plan.md"
  - "V3 reference/manual-test-and-delivery-checklist.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_epic.md"
reflected_to: []
---

# 20260702t020503z-03-disc Phase 3 Quality Delivery Gate Model

## Delivery policy

- User-approved current policy: one PR for the Epic by default.
- Issue-level PR splitting is not planned.
- If 1PR delivery becomes impractical during planning, reconsider at that time and record evidence.
- Final critical Issue owns Epic-wide quality gate, manual tests, review repair loop, and PR delivery readiness.

## Required quality dimensions

- requirement/design/plan consistency
- Initiative template correctness
- Epic template correctness
- planning skill correctness
- Epic execution skill correctness
- handoff completeness
- artifact/canonical boundary correctness
- automated tests
- manual tests
- dogfooding mirror impact
- PR readiness

## Suggested automated gates

- `uv run pytest tests/unit`
- `uv run pytest tests/cli_runtime`
- `make lint`
- `uv run pytest`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync`

Record unavailable or inappropriate commands in `report.md`.

## Manual test policy

- Use `manual-tests/` only for local trial workspaces.
- Initialize independent Git repos inside trial dirs when SpecDock state is needed.
- Do not track raw manual-test fixtures/logs/captures in the parent repo.
- Summarize evidence in the relevant report/artifact.

## Minimum manual scenarios

- new Initiative scaffold uses updated templates
- new Epic scaffold uses updated templates
- Initiative/Epic planning skills point to correct workflows and reviewer gates
- Epic execution skill can coordinate downstream Issue readiness
- `artifacts/` is recommended for new working artifacts
- legacy `discussions/` is preservation, not primary new destination
- Initiative/Epic templates do not include Issue-level TDD cycles or private implementation details
- generated/dogfooding docs remain coherent after validate/sync

## Adoption target

- `requirement.md`:
  - Adopt final delivery acceptance criteria.
- `plan.md`:
  - Adopt final critical Issue responsibilities and 1PR policy.
- `report.md`:
  - Record final quality evidence and PR readiness.
