---
種別: 設計書ドラフト（Issue）
ID: "iss-00232"
タイトル: "Enforce Blocker Centric PR Repair And Rereview"
関連GitHub: ["#232"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00232 Draft Design

## 設計方針
- PR Blocker Engine は review observation の raw evidence を受け、risk decision を deterministic policy で行う。
- P2/P3 は default non-blocking。protected + machine evidence の P2 のみ promoted blocker。
- Repair attempt limit は stagnation signal であり risk acceptance ではない。

## 変更対象
- Provider:
  - `domain/review_policy.py` finding disposition / protected domain / ReviewCoverage。
  - `application/evaluate_review_coverage.py`
  - repair batch / merge-prepared decision integration。
  - presentation of blocker summary。
- Dogfooding mirror:
  - review generation / repair evidence projections。

## Policy
- P0/P1 -> blocker。
- P2 protected + machine evidence -> promoted blocker。
- P2 non-protected -> no-action / follow-up。
- stale reviewed SHA -> not current repair input。
- blocker fix -> fresh re-review。

## 検証
- finding matrix tests。
- P2-only no push / no trigger。
- promoted P2 requires repair / re-review。
- repeated same finding -> automation-stalled。
- merge-prepared blocked while valid blockers remain。
- typed enum/value objects for MyPy / Ruff baseline。

## Handoff
- I07 consumes review quality corpus and blocker metrics。
