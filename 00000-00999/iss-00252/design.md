---
種別: 設計書（Issue）
ID: "iss-00252"
タイトル: "Compile Grade Aware Issue Planning Guidance"
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00252 Compile Grade Aware Issue Planning Guidance — Issue 設計書（Strict）

## 1. Strict とする理由

Issue planning guidance は agent の authoring behavior を変える workflow contract であり、後続 G2 / G3 / G4 が依存する。テンプレート / skill / workflow surface に影響するため strict grade とする。

## 2. 設計要約

- `[N]` `20260630t111316z-adr` を normative source として guidance を組み立てる。
- `[N]` guidance は grade 別 matrix と共通ルールを含む。
- `[N]` Lite automatic default 禁止、unknown / ambiguous は Standard 以上、manual escalation は authority override ではないことを明示する。
- `[N]` guidance は G2 / G3 が参照する role routing / evidence wording を提供するが、routing enforcement 自体は行わない。

## 3. Guidance 構成

| Section | 内容 | 後続依存 |
|---|---|---|
| Grade selection | Lite / Standard / Strict / Critical の判断材料 | G4 smoke |
| Authority split | `authorized_profile` と manual escalation の分離 | G2 draft routing |
| Requirement authoring | main orchestrator authority と risk facts | all |
| Design authoring | specialist 推奨 / 原則必須 / fallback | G2 / G3 |
| Plan authoring | planner 推奨 / 原則必須 / validation ladder | G3 / G4 |
| Review / report evidence | fresh spec-reviewer と report 記録 | G3 |

## 4. 変更候補

- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/phase_requirement.md`
- `src/spec_dock/assets/spec_dock/docs/phase_design.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- guidance compiler / presentation text if runtime owns the current issue-planning handoff
- dogfooding mirror under `spec-dock/docs/` and `.agents/`

## 5. Traceability

| 要件 | 設計 |
|---|---|
| AC-001 | Grade matrix section |
| AC-002 / AC-003 | Grade selection rules |
| AC-004 | Authority split section |
| AC-005 / AC-006 | Specialist routing wording |
| AC-007 | stable downstream wording |

## 6. 非対象

- R0 の readiness classifier 修正。
- G2 の `new doc` routing implementation。
- G3 の report evidence enforcement。
- G4 の smoke test full matrix。
