---
種別: 設計書（Issue）
ID: "iss-00254"
タイトル: "Add Grade Aware Spec Review And Evidence Gates"
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00254 Add Grade Aware Spec Review And Evidence Gates — Issue 設計書（Strict）

## 1. Strict とする理由

review / evidence gate は canonical phase promotion と issue readiness に影響する workflow contract である。draft artifact と canonical artifact の authority 境界を守るため strict grade とする。

## 2. 設計要約

- `[N]` Fresh `spec-reviewer` gate はすべての grade で必要。
- `[N]` delegated draft は Evidence Adoption Ledger なしに canonical docs へ採用できない。
- `[N]` Standard は specialist use / skip reason を report に残す。
- `[N]` Strict / Critical は specialist unavailable / fallback evidence を report に残す。
- `[N]` stale draft / stale reviewer / missing adoption evidence は readiness block とする。

## 3. Gate model

| Gate | 入力 | pass 条件 | fail / block |
|---|---|---|---|
| Draft Adoption Gate | discussion draft, canonical docs, report | EAL entry with adopted / partially adopted / rejected / deferred rationale | adoption claim without ledger |
| Fresh Spec Review Gate | canonical requirement/design/plan/report | latest canonical docs after adoption reviewed as pass | stale reviewer or missing review |
| Grade Evidence Gate | grade, specialist use, fallback | grade-specific evidence recorded | missing skip/fallback/manual evidence |
| Readiness Evidence Gate | report evidence, validator | required evidence present or explicit no-op reason | missing evidence |

## 4. 配置候補

- `workflow_spec_authoring.md`
- `phase_requirement.md`
- `phase_design.md`
- `phase_plan.md`
- issue planning skill guidance
- issue / epic report templates where evidence ledgers are defined
- domain readiness link if report evidence is classified by runtime

## 5. 要件追跡

| 要件 | 設計 |
|---|---|
| AC-001 | Fresh Spec Review Gate |
| AC-002 / AC-003 | Draft Adoption Gate |
| AC-004 | Grade Evidence Gate |
| AC-005 | Readiness Evidence Gate |
| AC-006 | draft self-claim prohibition |

## 6. 非対象

- G3 は draft generation の source routing を実装しない。
- G3 は code-reviewer / qa-reviewer の PR policy を変更しない。
- G3 は report evidence を捏造せず、未実施は未実施として記録させる。
