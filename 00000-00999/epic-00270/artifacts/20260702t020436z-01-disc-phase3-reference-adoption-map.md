---
種別: disc
ID: "20260702t020436z-01-disc"
タイトル: "Phase 3 Reference Adoption Map"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-01"
  - "20260702t014409z-research"
  - "20260702t015700z-interview"
authority: "proposed"
derived_from:
  - "artifacts/20260702t014409z-01-phase3-v3-planning-pack-full-intake.md"
  - "artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md"
reflected_to: []
---

# 20260702t020436z-01-disc Phase 3 Reference Adoption Map

## 対象論点

- V3 ZIP の情報を、canonical docs に全文貼りせず、コーディングエージェントが参照しやすい流路へ分ける。
- Canonical docs は採用判断・境界・Issue slicing policy・handoff package・acceptance/gate を持つ。
- 詳細分析、playbook、例、補助判断は scope-local `artifacts/` または ADR 候補へ分離する。

## V3 source routing

| V3 source | 主な用途 | 反映先 |
|---|---|---|
| `codex-handoff.md` | Epic mission, hard guardrails, final outcome | requirement/design/plan summary |
| `epic/epic-upstream-planning-governance-and-templates-v2.md` | Epic purpose, scope, issue list, final gate | requirement/plan |
| `epic/epic-level-planning-analysis.md` | scope-layering, artifact responsibility, final delivery policy | design/plan |
| `reference/upstream-abstraction-model.md` | Initiative/Epic/Issue/Plan/Report ownership model | design |
| `reference/discovery-to-canonical-specs.md` | artifacts are evidence, adoption rule | design/report |
| `reference/initiative-design-playbook.md` | Initiative template target model | design + Issue 01 handoff |
| `reference/epic-design-playbook.md` | Epic template target model | design + Issue 02 handoff |
| `reference/epic-to-issue-slicing-and-handoff.md` | design slice catalog, Issue handoff package, suggested grade | plan |
| `reference/issue-tdd-handoff-model.md` | upstream-to-Issue TDD handoff boundary | plan + Issue handoff |
| `reference/reviewer-anti-patterns.md` | scope drift and review heuristics | design/plan/test guidance |
| `issues/*.md` | baseline implementation slices | plan, but flexible under user-approved gate |
| `reference/manual-test-and-delivery-checklist.md` / `quality-gate-plan.md` | final critical Issue and PR readiness | plan/report |

## Split artifact map

- `20260702t020503z-01-disc-phase3-scope-authority-model.md`
  - Scope ownership, decision radius, canonical vs artifact authority.
- `20260702t020503z-disc-phase3-initiative-epic-template-model.md`
  - Initiative/Epic template target shape.
- `20260702t020503z-02-disc-phase3-issue-slicing-handoff-model.md`
  - Issue slicing, handoff package, readiness criteria.
- `20260702t020503z-03-disc-phase3-quality-delivery-gate-model.md`
  - Final quality Issue, manual tests, 1PR delivery.
- `20260702t020436z-decision-candidate-phase3-canonical-reference-flow-decision.md`
  - Candidate decision for how canonical docs refer to artifacts and ADRs.

## Adoption proposal

- `requirement.md`:
  - Adopt mission, scope, non-goals, final acceptance, current Phase 1/2 background.
- `design.md`:
  - Adopt upstream abstraction boundaries, artifact-to-canonical adoption, target template/workflow model.
- `plan.md`:
  - Adopt baseline 6 Issues, flexible slicing gate, handoff package, final quality/1PR delivery gate.
- `report.md`:
  - Record adoption of V3 raw intake, repo survey, answered interviews, and any split artifacts used.
- ADR:
  - Use only for decisions that need durable future reference beyond this Epic's plan.

## Non-adoption guardrails

- Do not copy all V3 prose into canonical docs.
- Do not ignore V3 references and redesign from scratch.
- Do not let raw artifact text override canonical docs after adoption.
- Do not create decision-only execution Issues.
- Do not make `artifacts/` canonical authority.

## Next action

- Reflect the user-approved Option B detail-level policy in `report.md` Evidence Adoption Ledger.
- Use this map when drafting `requirement.md`, `design.md`, and `plan.md`.
