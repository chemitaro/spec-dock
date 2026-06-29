---
種別: 要件定義書（Issue）
ID: "iss-00233"
タイトル: "Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry"
関連GitHub: ["#233"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00233 Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry — 要件定義

## 目的
- Dynamic Workflow Resource Allocation の初期 rollout を、既存 Issue 互換性、observability、future Auto-Lite readiness の証跡まで含めて閉じる。
- 初期 rollout では automatic Lite default を有効化せず、Lite は explicit opt-in + evidence gate の場合だけ authorized されることを維持する。

## 背景・現状
- I01〜I06 で assurance contract、workflow runbook、planning composition、context routing、trusted review policy、blocker-centric PR repair が実装済み。
- 残課題は、これらを rollout / compatibility / telemetry surface として利用者と将来の agent が確認できる状態にすること。
- 親 Epic では E-AC-013 を I07 owner とし、I06 は blocker fingerprint evidence を prerequisite として提供する。

## スコープ
- 必須:
  - `assurance` JSON 出力に future automatic Lite default の readiness report を含める。
  - `workflow next` の missing assurance path が strict-legacy authority で継続できることを検証する。
  - PR observation wait が repeated blocker fingerprint を `automation_stalled` / human gate として operator に出すことを検証する。
  - automatic Lite default が初期 rollout で enabled にならず、採用には accepted ADR / policy version bump / rollout Issue / telemetry gate が必要であることを機械可読にする。
  - automation-stalled は merge-prepared ではなく human gate / redesign の対象として report 可能にする。
- 禁止:
  - 初期 rollout で automatic Lite default を有効化しない。
  - 既存 Issue 全量 backfill や canonical artifact 自動改変を行わない。
  - Codex Action production migration や auto-merge は行わない。
- 対象外:
  - 実 telemetry storage / retention backend。
  - 本番 PR 上の長期計測。

## 受け入れ条件
- AC-001: Legacy compatibility
  - 前提: active Issue に `assurance.json` がない。
  - 操作: `assurance verify --format json` または `workflow next` を実行する。
  - 期待結果: strict-legacy mode / strict authority が返り、existing workflow / strict obligations で継続可能である。
- AC-002: Auto-Lite readiness without default enablement
  - 前提: adaptive assurance contract が valid。
  - 操作: `assurance show|verify|classify --format json` を確認する。
  - 期待結果: `auto_lite_readiness.automatic_lite_default_enabled` は `false` で、future adoption requirements と rollback mode が出力される。
- AC-003: Telemetry / efficiency evidence surface
  - 前提: classification が Lite candidate / Standard / Strict / Critical のいずれかになる。
  - 操作: JSON payload を確認する。
  - 期待結果: Lite candidate / authorized、hard triggers、unknown facts、required telemetry fields、missing metrics summary、future efficiency metrics の出力契約がある。
- AC-004: Automation stalled
  - 前提: repair loop が同じ blocker fingerprint で停滞する。
  - 操作: rollout readiness report を確認する。
  - 期待結果: `automation_stalled.present=true` が出力され、merge-prepared ではなく human gate / redesign routing として表現される。

## 例外・エッジケース
- EC-001: Contract missing
  - 期待: auto-lite readiness report は strict-legacy missing classification と整合し、Lite を authorize しない。
- EC-002: Hard trigger present
  - 期待: Lite candidate / opt-in / evidence gate があっても authorized profile は hard trigger 以上に escalation される。
- EC-003: Missing metrics
  - 期待: future automatic Lite default は enabled にならず、missing metrics summary が adoption blocker として残る。

## 用語
- Auto-Lite readiness report:
  - 初期 rollout で automatic Lite default を有効化せず、将来採用に必要な条件と rollback 条件を記録する機械可読 report。
- strict-legacy:
  - `assurance.json` がない既存 Issue を既存 strict workflow として扱う互換 mode。
