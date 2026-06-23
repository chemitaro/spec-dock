---
種別: research
ID: "20260623t011746z-research"
タイトル: "Deep Consultant Lite Rollout Task Package"
状態: "draft"
作成者: "Codex"
最終更新: "2026-06-23"
親: ["epic-00224"]
関連:
  - "20260623t011349z-research"
  - "20260623t011352z-interview"
authority: "evidence"
derived_from:
  - "user request to delegate system-design analysis to deep-consultant"
reflected_to: []
---

# 20260623t011746z-research Deep Consultant Lite Rollout Task Package

## 依頼理由

- 前回の clarification では、Lite profile rollout をユーザーへ確認する質問として扱った。
- ユーザーから、これはユーザー体験の好みではなく、SpecDock scripts と SpecDock を操作する agent workflow の system-design / best-practice 判断であると補正があった。
- そのため、ユーザー意図の質問ではなく deep-consultant の source-grounded analysis に回す。

## Consultant への判断対象

- Option A: Conservative rollout
  - Standard default.
  - Lite は all-positive eligibility が揃った場合のみ opt-in / evidence-gated。
- Option B: Aggressive Lite automation
  - 新規 Issue では routine / low-risk と判定できる場合に Lite を自動適用し、risk detected で escalation。
- Option C: Hybrid acceptance gate
  - 実装 rollout は A で始める。
  - Epic success criteria には safe Lite automation predicates と telemetry gate の定義を含める。
  - future automatic Lite default は evidence gate を通ってからにする。

## Consultant に依頼した観点

- system-design best practice として推奨案を出す。
- safety、false positives / false negatives、observability、migration、implementation slicing、agent failure modes から分析する。
- 採用時の requirement / design / plan implications を明示する。
- 追加 user interview が本当に必要か判断する。

## 想定される採用先

- `requirement.md`
  - Lite / Standard default、success criteria、non-scope、rollout acceptance。
- `design.md`
  - classification policy、escalation、telemetry、rollback、generated state boundary。
- `plan.md`
  - I01/I02/I07 の scope、completion gate、dependency order。
- `report.md`
  - Evidence Adoption Ledger / Spec Authoring Gate。
