---
種別: 設計書ドラフト（Issue）
ID: "iss-00227"
タイトル: "Introduce Assurance Contract And Classification Runtime"
関連GitHub: ["#227"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00227 Draft Design

## 設計方針
- Domain-first に `AssuranceContract`、`Classification`、`SourceBinding`、`ObligationSet` の最小 model を作る。
- Classification は pure function とし、filesystem / GitHub / CLI に依存しない。
- Infra は issue-local `assurance.json` の read/write と schema validation を担当する。

## 変更対象
- Provider:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/classify_assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/assurance_text.py`
  - `src/spec_dock/assets/spec_dock/system/assurance/**`
- Dogfooding mirror:
  - `spec-dock/scripts/spec_dock_runtime/**`
  - `spec-dock/system/assurance/**`

## Interface
- `spec-dock assurance show --format text|json`
- `spec-dock assurance classify --stage requirement`
- `spec-dock assurance verify`

## 検証
- classification truth table。
- Lite predicate true/false/unknown。
- hard trigger monotonic escalation。
- schema validation / deterministic output。
- existing issue without contract -> strict-legacy detection。
- MyPy / Ruff baseline を崩さない typed modules。

## Handoff
- I02 は `AssuranceContract` / `authorized_profile` / strict-legacy detection を読む。
- I03 は source binding field を拡張して approved/stale を扱う。
