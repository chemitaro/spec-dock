---
種別: 要件定義書ドラフト（Issue）
ID: "iss-00230"
タイトル: "Compile Step Assurance Agent Routing And Context Policy"
関連GitHub: ["#230"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00230 Draft Requirement

## 目的
- Step facts、Issue-wide Assurance、agent role、task kind から worker、reasoning effort、context mode、verification、reviewer を含む execution Runbook を生成する。
- 実行系 agent の context affinity と reviewer / consultant clean-room independence を両立する。

## スコープ
- 必須:
  - Step Assurance schema / compiler。
  - global ∪ local ∪ discovered obligations。
  - `context-routing-policy.json` と schema。
  - `recent_fork / bounded_packet / clean_room / minimal_packet`。
  - Context Policy Resolver。
  - Context Packet / Reviewer Evidence Packet compiler。
  - consultant first-pass / arbitration contract。
  - worker continuation policy。
  - bounded return contract and returned evidence refs observability。
- 禁止:
  - GitHub PR review trigger。
  - PR finding blocker policy。
  - private reasoning の保存 / 転送。

## Trace
- closes: E-RQ-007, E-RQ-008, E-RQ-015〜021, E-AC-007, E-AC-017〜021。

## 受け入れ条件
- AC-001: docs-only / runtime behavior / migration / security-sensitive step で worker、reasoning、context、verification、reviewers が異なる。
- AC-002: reviewers は clean-room packet を使用し、author transcript / previous verdict を含まない。
- AC-003: consultant first pass は main / architect 推奨案を含まない。
- AC-004: same source binding / scope / risk では worker continuation が可能で、変更後は reset される。
- AC-005: child return payload に raw logs / private reasoning が混入しない。

## 依存
- Upstream: iss-00229。
- Downstream: iss-00232, iss-00233。

## 静的解析前提
- Policy schema / packet model は typed value object と validation boundary を持ち、MyPy / Ruff に耐える shape にする。
