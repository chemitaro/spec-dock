---
種別: 設計書（Issue）
ID: "iss-00255"
タイトル: "Add Grade Aware Issue Authoring Smoke Tests"
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00255 Add Grade Aware Issue Authoring Smoke Tests — Issue 設計書（Strict）

## 1. Strict とする理由

G4 は R0〜G3 の統合品質を保証する closure slice であり、workflow readiness、template routing、review evidence、provider / dogfooding parity にまたがる。個別 Issue の欠落を検出する役割を持つため strict grade とする。

## 2. 設計要約

- `[N]` Grade Smoke Fixture Builder は Lite / Standard / Strict / Critical の代表 Issue fixture を作る。
- `[N]` Template Gate Smoke は profile template materialization と M99 gate の有無を検査する。
- `[N]` Draft Routing Smoke は `authorized_profile` と draft source template の対応を検査する。
- `[N]` Readiness Smoke は placeholder / heading-only / stale evidence の false positive を検査する。
- `[N]` Evidence Smoke は delegated specialist evidence、Evidence Adoption Ledger、fresh review evidence の最低限の組み合わせを検査する。
- `[N]` Parity Smoke は provider source と dogfooding mirror の docs / templates の整合を検査する。

## 3. Smoke surface

| Surface | 入力 | 観測点 | 対応 AC |
|---|---|---|---|
| Lite template smoke | Lite fixture | commit gate / full static analysis mandatory がない | AC-001 |
| Standard+ M99 smoke | Standard / Strict / Critical fixture | M99 static analysis / lint / tests / report / commit gate がある | AC-002 |
| Draft routing smoke | classified Issue + `.assurance.json` | `draft-design` / `draft-plan` source profile | AC-003 |
| Fail-closed smoke | missing / invalid / stale `.assurance.json` | no-write and reason | AC-004 |
| Readiness smoke | placeholder / heading-only / stale evidence fixture | not execution-ready | AC-005 |
| Evidence smoke | report evidence fixture | specialist / EAL / reviewer evidence relation | AC-006 |
| Parity smoke | provider / dogfooding paths | intended parity or documented exception | AC-007 |

## 4. 配置候補

- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_workflow.py`
- `tests/unit/domain/test_workflow_state.py`
- `tests/unit/infra/test_init_update.py`
- provider docs / templates under `src/spec_dock/assets/spec_dock/...`
- dogfooding docs / templates under `spec-dock/...`

## 5. 要件追跡

| 要件 | 設計 |
|---|---|
| AC-001 | Lite template smoke |
| AC-002 | Standard+ M99 smoke |
| AC-003 | Draft routing smoke |
| AC-004 | Fail-closed smoke |
| AC-005 | Readiness smoke |
| AC-006 | Evidence smoke |
| AC-007 | Parity smoke |
| AC-008 | report evidence |

## 6. 非対象

- G4 は production telemetry backend を追加しない。
- G4 は external GitHub repository を必須にしない。
- G4 は R0〜G3 の主要ロジックを肩代わりしない。
