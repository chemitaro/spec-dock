---
種別: 要件定義書ドラフト（Issue）
ID: "iss-00233"
タイトル: "Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry"
関連GitHub: ["#233"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00233 Draft Requirement

## 目的
- Adaptive workflow を shadow、opt-in、Standard default へ段階導入し、legacy compatibility、observability、rollback、Auto-Lite readiness を閉じる。

## スコープ
- 必須:
  - shadow classification。
  - explicit opt-in。
  - new Issue Standard default。
  - Lite manual / evidence-gated activation。
  - `auto-lite-readiness report`。
  - strict-legacy adapter。
  - event / metrics projection。
  - benchmark / review-quality corpus。
  - provider / mirror / installer / docs / validate / sync。
  - rollback runbook。
- 禁止:
  - automatic Lite default の有効化。
  - existing Issue 全量 backfill。
  - Codex Action production migration。

## Trace
- closes: E-RQ-012, E-RQ-013, E-RQ-014, E-AC-014, E-AC-015, E-AC-016。

## 受け入れ条件
- AC-001: Existing Issue without `assurance.json` は strict-legacy path で動作し、canonical artifact を silent rewrite しない。
- AC-002: new Issue は Standard provisional path で dogfooding 成功する。
- AC-003: `auto-lite-readiness report` が predicates、telemetry gate、promotion / rollback 条件を示し、automatic Lite default は無効のままである。
- AC-004: benchmark が agent invocation、review generation、P2 repair push の改善を示す。
- AC-005: provider / mirror / installer / docs / tests が同期し、`validate` / `sync` が通る。

## 依存
- Upstream: iss-00228, iss-00229, iss-00230, iss-00231, iss-00232。

## 静的解析前提
- rollout config / metrics projection は typed schema と missing metrics semantics を持ち、MyPy / Ruff baseline を崩さない。
