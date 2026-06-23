---
種別: 設計書ドラフト（Issue）
ID: "iss-00233"
タイトル: "Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry"
関連GitHub: ["#233"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00233 Draft Design

## 設計方針
- Rollout is staged: shadow -> explicit opt-in -> selected dogfooding -> Standard default。
- Automatic Lite default remains out of initial rollout。
- Existing Issues remain strict-legacy unless explicitly migrated。

## 変更対象
- Provider:
  - rollout / repository mode config。
  - event / metrics projection。
  - auto-lite-readiness report projection。
  - installer / update parity。
  - docs / references / doctor。
- Dogfooding mirror:
  - golden workflow corpus。
  - generated events / reports ignored。

## Metrics
- invocation count by role。
- reasoning effort / context mode。
- token metrics where available; missing explicit。
- review generation count。
- P2 repair push count。
- `lite_candidate` / `lite_authorized` count。
- escalation rate。
- wall-clock proxy。

## Rollback
- Repository config can force legacy workflow。
- `assurance.json` can remain as history while execution authority ignores adaptive mode。
- generated state can be deleted and recompiled。

## 検証
- existing fixture unchanged。
- new fixture Standard default。
- generated state clean。
- auto-lite-readiness report shows adoption / rollback conditions。
- benchmark shows reduced invocation / P2 loops without dropping required quality gates。
- provider / mirror / installer / docs / tests sync。
- static analysis baseline remains clean after MyPy / Ruff configuration lands。
