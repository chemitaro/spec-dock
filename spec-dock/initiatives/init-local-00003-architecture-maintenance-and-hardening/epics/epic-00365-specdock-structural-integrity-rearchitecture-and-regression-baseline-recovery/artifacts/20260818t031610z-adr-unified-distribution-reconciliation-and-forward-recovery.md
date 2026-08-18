---
種別: ADR（Architecture Decision Record）
ID: "20260818t031610z-adr"
タイトル: "Unified Distribution Reconciliation And Forward Recovery"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-18"
親: ["epic-00365"]
authority: "draft"
accepted_authority: ""
accepted_at: ""
accepted_by: ""
mirror_eligible: false
derived_from: []
reflected_to: []
---

# 20260818t031610z-adr Unified Distribution Reconciliation And Forward Recovery

architecture / contract / migration の判断候補を記録します。明示的に `accepted` となった ADR だけが durable authority になり得ます。original は `artifacts/` に残り、legacy `discussions/` も accepted ADR の mirror source として扱えます。

## Context

- 判断が必要な背景と制約:
  - ...

## Decision

- draft の間は未決。明示的な判断後に結論を記録する。
- accepted にするときだけ、次を明示する:
  - `状態: "accepted"`
  - `authority: "accepted"`
  - `accepted_authority: "accepted ADR"`
  - `accepted_at: "2026-08-18"`
  - `accepted_by: "<DECISION_OWNER>"`
  - `mirror_eligible: true`

## Options

- 検討した選択肢と trade-off:
  - ...

## Consequences

- 影響、移行、または見直し条件:
  - ...

## References

- 根拠と反映先:
  - ...
