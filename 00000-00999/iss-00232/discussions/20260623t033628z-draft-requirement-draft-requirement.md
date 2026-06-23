---
種別: 要件定義書ドラフト（Issue）
ID: "iss-00232"
タイトル: "Enforce Blocker Centric PR Repair And Rereview"
関連GitHub: ["#232"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00232 Draft Requirement

## 目的
- P0 / P1 と machine-validated blocker だけを repair loop へ入れ、P2 / P3 noise による修正・push・re-review 反復を抑止する。

## スコープ
- 必須:
  - finding priority normalization。
  - P0/P1 blocker。
  - P2 default no-action / follow-up。
  - protected domain + machine evidence promotion。
  - stale reviewed SHA exclusion。
  - fresh re-review matrix。
  - stagnation / automation-stalled。
  - merge-prepared predicate。
- 禁止:
  - automatic merge。
  - 修正回数上限を risk acceptance とみなすこと。
  - P2 comment zero を merge condition にすること。

## Trace
- closes: E-RQ-010, E-RQ-011, E-AC-011, E-AC-012, E-AC-013。

## 受け入れ条件
- AC-001: P2/P3 only では repair / push / fresh review を開始しない。
- AC-002: valid P1 fix 後は fresh review が要求される。
- AC-003: protected P2 + failing regression test は promoted blocker になる。
- AC-004: repair stagnation は automation-stalled / human gate になり、merge-prepared にならない。

## 依存
- Upstream: iss-00230, iss-00231。
- Downstream: iss-00233。

## 静的解析前提
- Finding disposition / review coverage は typed enums/value objects とし、priority string の分岐を局所化する。
