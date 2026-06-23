---
種別: 設計書ドラフト（Issue）
ID: "iss-00229"
タイトル: "Compose Profile Aware Planning Artifacts"
関連GitHub: ["#229"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00229 Draft Design

## 設計方針
- Artifact Composer は policy fragment と canonical inputs から section を単調合成する。
- Existing substantive body は自動変更しない。
- Source binding mismatch は stale とし、execution handoff を止める。

## 変更対象
- Provider:
  - `application/compose_artifacts.py`
  - `domain/assurance.py` source binding status extension。
  - `infra/assurance_store.py` source hash verification。
  - `src/spec_dock/assets/spec_dock/templates/assurance/**`
  - fragment manifest / schema。
- Dogfooding mirror:
  - `spec-dock/templates/assurance/**`
  - generated section marker behavior。

## Composition Rules
- pristine scaffold: full materialization allowed。
- existing substantive section: preserve body, add missing section only。
- escalation: additive section + downstream invalidation。
- downgrade: no automatic deletion。

## 検証
- Profile fixture golden files。
- idempotence twice compile no diff。
- no-overwrite tests。
- source hash mismatch blocks execution Runbook。
- MyPy / Ruff friendly typed fragment manifest and parser boundary。

## Handoff
- I04 uses composed plan / step facts。
- I07 uses composer behavior in rollout and legacy compatibility tests。
