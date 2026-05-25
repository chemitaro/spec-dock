---
種別: disc
ID: "20260524t150916z-disc"
タイトル: "Fresh Consultant Review of V2 Discussion Direct Write Model"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
親: ["iss-00127"]
関連: []
authority: "proposed"
derived_from:
  - "20260524t133442z-adr-flat-scope-local-discussion-drafts.md"
  - "20260524t150117z-disc-scoped-discussion-draft-authoring-requirement-draft-v2.md"
  - "fresh deep-consultant review 2026-05-25"
reflected_to: []
---

# 20260524t150916z-disc Fresh Consultant Review of V2 Discussion Direct Write Model

## 位置づけ
- この document は、V2 discussion direct-write model に対する fresh deep-consultant review の統合記録である。
- consultant には、proposal-only を標準採用しないこと、sub-agent が scope-local `discussions/` 直下に直接 draft / analysis / report Markdown を作成・編集できることを前提制約として渡した。
- この document は canonical artifact ではない。V2 draft と canonical docs へ反映するための discussion evidence である。

## 議題 (必須)
- proposal-only を採用せず、sub-agent discussion direct-write を採用する V2 方針に対して、残る harness / context / implementation migration リスクを整理する。

## 背景 (必須)
- V2 は、canonical docs single-writer と sub-agent discussion direct-write を分離する。
- sub-agent の direct write は、context compaction や伝言ゲームで失われる設計情報を file-based context として永続化するための設計である。
- 一方で direct write は安全境界そのものではないため、diff guard、adoption ledger、stale handling、authority claim 禁止で補完する必要がある。

## 選択肢 (必須)
- Option A: V2 をそのまま canonical docs に昇格する
  - Pros:
    - すでに proposal-only 不採用と discussion direct-write の理由が明記されている。
  - Cons:
    - direct write の forbidden claim / existing file overwrite / stale handling がまだ弱い。
    - sub-agent が adoption や reflection を自己申告できる余地が残る。
- Option B: V2 を採用しつつ、direct-write guardrail を補強してから canonical docs に昇格する
  - Pros:
    - sub-agent direct-write の効率性と canonical authority boundary を両立しやすい。
    - proposal-only を採らない方針を維持しつつ、fresh consultant の主要懸念を閉じられる。
  - Cons:
    - V2 draft と後続 canonical docs の記述量は少し増える。

## 推奨案 (必須)
- Option B を採用する。
- V2 の根本方針、つまり sub-agent scope-local `discussions/` direct-write は維持する。
- ただし direct write は「安全境界」ではなく「persistent proposal / evidence channel」であると明記し、以下を補強する。
  - sub-agent draft は原則新規作成とし、既存 discussion file の編集は orchestrator が明示指定した proposed draft のみに限定する。
  - accepted ADR / superseded / stale / rejected / adopted 済み discussion は sub-agent が直接編集しない。
  - sub-agent-created draft は `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` を自己主張しない。
  - `adoption_status` と `reflected_to` の authoritative source は main orchestrator の `report.md` adoption ledger である。
  - required provenance として `created_by_role`、`scope_id`、`source_paths`、`intended_targets`、`adoption_status: unreviewed`、`reflected_to: []` を持つ。
  - allowed diff は target scope の `discussions/` 直下にある naming-rule compliant Markdown create/update に限定する。
  - forbidden diff があれば delegated output は rejected / ineligible であり、canonical adoption できない。

## 未決事項 (任意)
- `report.md` adoption ledger の section name と exact field set。
- post-run diff guard を runtime helper として実装するか、初回は orchestrator workflow docs に閉じるか。
- static adapter で scope-local `discussions/` write をどこまで enforce するか。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - V2 draft に direct-write guardrail、required provenance、orchestrator-only adoption/reflection を追記する。
  - canonical docs 作成時に、sub-agent direct-write の許可範囲と禁止範囲を明確化する。
- 追加で作る discussion docs:
  - 現時点では不要。
