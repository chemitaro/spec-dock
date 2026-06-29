---
種別: 設計書ドラフト（Issue）
ID: "iss-00230"
タイトル: "Compile Step Assurance Agent Routing And Context Policy"
関連GitHub: ["#230"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00230 Draft Design

## 設計方針
- Step Assurance Compiler は issue global obligations、step local facts、discovered risk の和集合から effective obligations を作る。
- Context Policy Resolver は Assurance Profile / reasoning effort と独立した axis として context mode を決定する。
- Reviewer / consultant first pass は clean-room を fail-closed に扱う。

## 変更対象
- Provider:
  - `domain/context_routing.py`
  - `domain/runbook.py` context contract extension。
  - `application/compile_step_assurance.py`
  - `application/compile_context_packet.py`
  - `infra/context_policy_store.py`
  - `infra/context_packet_store.py`
  - `src/spec_dock/assets/spec_dock/system/assurance/context-routing-policy.json`
  - schema under `system/assurance/schemas/`
- Dogfooding mirror:
  - `spec-dock/system/assurance/context-routing-policy.json`
  - `spec-dock/.agent/context-packets/**` ignored。

## Context Modes
- `recent_fork`: execution worker affinity。
- `bounded_packet`: fork unavailable or bounded specialist task。
- `clean_room`: reviewer / consultant first pass。
- `minimal_packet`: bounded command / spec-manager style task。

## 検証
- role routing matrix。
- clean-room exclusion tests。
- consultant blind-first-pass tests。
- worker continuation / reset tests。
- context packet stale invalidation。
- bounded return contract and returned evidence refs event。
- MyPy / Ruff friendly typed packet models。

## Handoff
- I06 consumes reviewer evidence / review coverage boundary。
- I07 consumes invocation evidence and context metrics。
