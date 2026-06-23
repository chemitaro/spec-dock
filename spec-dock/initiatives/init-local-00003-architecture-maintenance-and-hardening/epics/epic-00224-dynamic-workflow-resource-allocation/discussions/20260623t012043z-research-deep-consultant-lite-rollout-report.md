---
種別: research
ID: "20260623t012043z-research"
タイトル: "Deep Consultant Lite Rollout Report"
状態: "draft"
作成者: "deep-consultant"
最終更新: "2026-06-23"
親: ["epic-00224"]
関連:
  - "20260623t011746z-research"
  - "20260623t011352z-interview"
authority: "evidence"
derived_from:
  - "deep-consultant analysis on Lite rollout best practice"
reflected_to: []
---

# 20260623t012043z-research Deep Consultant Lite Rollout Report

## 結論

- 採用すべきは **Option C の強化版**。
- 初期実行は Option A と同じく、`Standard default` / `Lite` は all-positive eligibility + explicit opt-in + evidence-gated に固定する。
- Epic の成功条件には、将来の automatic Lite default に必要な safe predicates、shadow classification、telemetry gate、promotion 条件を含める。
- ただし、この Epic 内では automatic Lite を default 有効化しない。
- automatic Lite default の有効化は、観測証拠に基づく別 Issue、ADR、または policy version bump で行う。

## B を採用しない理由

- SpecDock runtime と agent workflow は、作業手順そのものの authority である。
- Lite false positive の損害が大きい。
  - Lite にしてはいけない Issue を Lite にすると、requirement / design / plan gate、reviewer independence、PR closure semantics を欠いたまま進む可能性がある。
  - 後から検出しても、失われた review / planning evidence を復元しにくい。
- Lite false negative は許容できる。
  - Standard に寄るだけなら token / time は増えるが、rollback や再分類で回復できる。
- Escalation は救済策であり、初期分類の安全性の代替ではない。
- `workflow next` / `assurance classify` / `Runbook` surface が未実装の現段階で automatic Lite default を入れると、agent が gate を省略しても runtime が十分に検出できない。

## Best-practice 原則

- false positive 回避を最優先にする。
- false negative は許容する。
- model confidence ではなく、runtime policy engine の three-valued predicate `true / false / unknown` で判定する。
- `lite_candidate` と `lite_authorized` を分離する。
  - `lite_candidate`: shadow measurement / telemetry 用。obligation を減らさない。
  - `lite_authorized`: obligation reduction に使える正式 profile。
- Runbook Compiler は `authorized_profile` だけを参照する。
- required predicate が false または unknown、hard trigger present、source binding stale、telemetry / policy evaluation unavailable の場合、Lite を authorize しない。

## リスク

- 初期の省力化効果は限定的になる。
  - これは意図的な tradeoff。
  - shadow 判定で「本来 Lite にできたが Standard で実行した」ケースを集め、将来の自動化判断を監査可能にする。
- telemetry gate が形骸化するリスクがある。
  - I07 は単なる metrics ではなく `auto-lite-readiness report` を成果物にする。
  - false positive candidates、escalation rate、P0/P1 escape、post-review blocker、wall-clock/token delta、missing metrics を明示する。

## Requirement wording seed

```text
- Standard is the authoritative default for new adaptive Issues.
- Lite classification has two distinct outcomes: `lite_candidate` for shadow measurement and `lite_authorized` for obligation reduction.
- Runtime MUST NOT authorize Lite when any required Lite predicate is false or unknown, any hard trigger is present, source binding is stale, or required telemetry/policy evaluation is unavailable.
- Initial rollout MUST NOT make automatic Lite the default. Automatic Lite default requires separate evidence-backed policy adoption after shadow and opt-in telemetry gates pass.
```

## Design wording seed

```text
- Model Lite eligibility as a three-valued policy result: true / false / unknown.
- Store `classification.proposed_profile`, `classification.authorized_profile`, `decision_source`, `unknown_facts`, `predicate_results`, and `evidence_refs`.
- Runbook Compiler MUST use only `authorized_profile`; shadow `lite_candidate` is emitted only to events/reports.
- Add rollout modes: legacy, shadow, opt-in, standard-default, auto-lite-experimental. Initial implementation supports auto-lite-experimental only as disabled future policy surface.
```

## Plan wording seed

```text
- I01: implement Standard default, Lite all-positive predicates, unknown fail-closed, and candidate-vs-authorized profile separation.
- I02-I04: ensure Runbook, artifact composition, and step routing ignore `lite_candidate` unless explicitly authorized.
- I07: produce shadow/opt-in telemetry and an auto-lite-readiness report; do not enable automatic Lite default as part of the initial Epic completion.
- Final completion: Standard default dogfooding succeeds, Lite opt-in is evidence-gated, and automatic Lite promotion criteria are defined with measured evidence and rollback conditions.
```

## 追加ユーザーインタビュー要否

- 不要。
- ユーザー補正により、この論点は UX preference ではなく system-design / best-practice 判断だと明確になった。
- Local source と draft package から結論を出せる。
- 次は質問ではなく、canonical `requirement.md` / `design.md` / `plan.md` への反映準備へ進む。
