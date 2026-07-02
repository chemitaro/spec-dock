---
種別: disc
ID: "20260702t020503z-01-disc"
タイトル: "Phase 3 Scope Authority Model"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-01"
  - "20260702t020436z-01-disc"
authority: "proposed"
derived_from:
  - "V3 reference/upstream-abstraction-model.md"
  - "V3 epic/epic-level-planning-analysis.md"
  - "V3 reference/discovery-to-canonical-specs.md"
reflected_to: []
---

# 20260702t020503z-01-disc Phase 3 Scope Authority Model

## Purpose

This artifact extracts the scope/authority model from V3 so downstream agents can use it without reading the raw ZIP intake.

## Adopted model candidate

| Scope | Owns | Must not own |
|---|---|---|
| Initiative | Strategic change, capability landscape, context ownership, source of truth, strategic invariants, transition architecture | Aggregate methods, Issue TDD cycles, private implementation structure |
| Epic | Capability/model envelope, lifecycle, cross-Issue invariants, contract portfolio, design slice catalog, Issue handoff | Product-wide source-of-truth changes, private helpers, detailed TDD cycles |
| Issue | One observable behavior or local model delta, local contract delta, verification implications | Redefining Epic envelope, broad Initiative decisions, unrelated refactors |
| Issue Plan | Milestones, Behavior Backlog, TDD cycles, validation ladder, report evidence mapping | New requirements, new design contracts, parent model changes |
| Report | Observed evidence, reviewer verdicts, deviations, adoption ledger, delivery evidence | Planned obligations or future architecture decisions |

## Canonical authority flow

```text
raw artifact / discovery
  -> synthesized artifact or decision candidate
    -> canonical requirement/design/plan or accepted ADR
      -> report.md Evidence Adoption Ledger
```

## Decision radius rule

- Multi-initiative or global architecture decisions belong to ADR / architecture docs.
- Multi-epic decisions within one Initiative belong to Initiative design.
- Multi-issue decisions within one Epic belong to Epic design.
- One-Issue decisions belong to Issue design.
- Execution sequencing belongs to Issue plan.
- Private implementation details belong to code/tests.

## Phase 3 implications

- Do not create an Issue whose only job is to define all planning boundaries.
- Do not let raw artifacts become implementation authority.
- Do not let Issue plans create new parent requirements/design decisions.
- Epic design must own the scope-layering model needed by downstream Issues.

## Adoption target

- `design.md`:
  - Adopt this as the Epic's scope and authority model.
- `plan.md`:
  - Use this to justify Issue slicing and no decision-only Issues.
- `report.md`:
  - Record adoption if used in canonical docs.
