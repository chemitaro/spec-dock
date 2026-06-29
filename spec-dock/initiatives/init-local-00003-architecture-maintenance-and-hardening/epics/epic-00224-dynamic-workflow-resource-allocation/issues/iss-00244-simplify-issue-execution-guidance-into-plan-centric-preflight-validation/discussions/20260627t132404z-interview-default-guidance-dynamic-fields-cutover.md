---
種別: interview
ID: "20260627t132404z-interview"
タイトル: "Default Guidance Dynamic Fields Cutover"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00244"]
関連:
  - "20260627t131746z-research"
  - "20260627t132248z-disc"
scope: "issue"
scope_id: "iss-00244"
created_at: "2026-06-27T13:24:04Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260627t131746z-research-plan-centric-guidance-requirement-preparation.md"
  - "20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md"
  - "oracle: gpt-5.5-pro extended via chatgpt-use, session iss-00244-requiremen-prep-analysis"
reflected_to: []
---

# 20260627t132404z-interview Default Guidance Dynamic Fields Cutover

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `guidance issue-execution` の output contract と受け入れ条件に、旧 dynamic fields の削除 / deprecated / legacy opt-in のどれを書くかが変わる。
  - `design.md`:
    - Runbook schema、presentation、`workflow.py`、`context_packets.py`、`context_routing.py`、test replacement の範囲が変わる。
  - `plan.md`:
    - 実装 step の分割、削除範囲、互換性 test、dogfooding validation が変わる。
  - `ADR`:
    - 現時点では不要想定。ただし互換性を長期維持する判断なら ADR 候補になり得る。
- chat 上の軽微な一問では足りない理由:
  - この回答により、default guidance から `selected_step` / `step_assurance` / `context_packets` を即時消すか、互換期間を置くかが決まり、要件・設計・テスト範囲が大きく変わるため。

## 質問の目的 (必須)
- 対象者:
  - human product owner / spec-dock maintainer
- 何を明確にする質問か:
  - `iss-00244` で、旧 dynamic guidance fields を default agent-facing contract からどの深さで外すか。
- 回答が後続判断へ与える影響:
  - hard cutover なら要件は単純化を強く固定し、JSON / Markdown / projection / tests から旧 field を削除する方向になる。
  - 互換期間ありなら、旧 field を deprecated / non-authoritative として残す schema / warning / tests が必要になる。

## 質問 (必須)
- pressure-test question:
  - 今回の主目的は agent が古い dynamic output を authority と誤認しないことなので、default output から旧 field を完全に外すべきか。
- 質問:
  - `iss-00244` では、`guidance issue-execution` の default Markdown / JSON / runbook projection から `selected_step`、`step_assurance`、`context_packets` を互換期間なしで削除する hard cutover として要件化してよいですか？
- 回答してほしいこと:
  - A: hard cutover でよい。
  - B: default では非表示にするが、deprecated / legacy option として短期的に残す。
  - C: default から外すが、context packet だけは明示 command / option として今回 issue 内で残す。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/docs/phase_plan_issue.md`: `plan.md` は planned contract / command queue、`report.md` は observed evidence ledger。
  - `spec-dock/docs/authoring/issue-plan.md`: implementation step は delegation contract、具体テストケース、report evidence destination、amendment trigger を持つ。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`: ready な `issue-execution` で dynamic execution context を compile する。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`: `plan.md` / `report.md` から `selected_step` と context packet を作る。
  - `tests/cli_runtime/test_workflow_context_routing.py`: 旧 dynamic model を期待している。
  - `20260627t132248z-disc`: hard cutover 寄り推奨。
- local context で解決できたこと:
  - default `guidance issue-execution` を step selector ではなく preflight validator にする方向は、ユーザー判断・Oracle・既存 docs で一致している。
  - generated projection は human/debug-only であり、agent authority ではない。
- まだ人間判断が必要な理由:
  - 旧 fields を即時削除するか、deprecated として残すかは、外部 / 既存 CLI consumer の互換性許容度に関わり、コードからだけでは判断できない。

## 回答案 (必須)
- Option A:
  - hard cutover。default Markdown / JSON / runbook projection から `selected_step` / `step_assurance` / `context_packets` を削除し、要件・設計・テストも新 contract に置換する。
- Option B:
  - default agent-facing Markdown からは消すが、JSON / projection に deprecated field として短期的に残し、non-authoritative warning を付ける。
- Option C:
  - default guidance からは消すが、context packet だけは今回 issue 内で明示 command / option に移す。

## Codex の分析 (必須)
- 判断軸:
  - agent が旧 output を authority と誤認するリスク。
  - output schema 破壊を許容できるか。
  - 今回 issue の scope を単純に保てるか。
  - context packet / clean-room evidence の将来価値を今回 issue に含める必要があるか。
- tradeoff:
  - Option A は最も単純で主目的に合うが、JSON consumer があれば破壊的。
  - Option B は互換性に優れるが、旧概念が残り、agent-facing confusion を完全に断てない。
  - Option C は将来拡張を残せるが、今回 issue の範囲が広がりやすい。
- リスク:
  - Option A でも `context_routing.py` の削除範囲を誤ると、別機能の将来価値を消す可能性がある。
  - Option B / C では、旧 field を「非 authority」と書いても agent が読み続ける可能性がある。
- 具体シナリオ / edge case:
  - `report.md` が stale でも、旧 `selected_step` が残っていると agent がその step に従う。
  - `current-context-packets.json` が古いのに、projection から再利用される。
  - deprecated JSON field を見たテスト / script が旧 contract を維持し続ける。

## Codex の推奨案 (必須)
- 推奨:
  - Option A: hard cutover。
- 理由:
  - ユーザーの問題定義は「旧 dynamic model の精度改善」ではなく「実装計画書に一本化して、agent が追随しやすい単純な model に戻すこと」である。
  - この branch / Epic はまだ main に merge されていないため、旧 branch 内 feature への互換性より、正しい contract へ切り替える価値が高い。
  - 旧 field を残すと、今回解消したい multi-authority / stale projection 問題が残る。
- 未回答時の影響:
  - 未回答のままでも Option A を仮定して requirement draft は作れるが、後で互換性方針が変わると設計・テスト計画の手戻りが大きい。

## ユーザー回答 (回答後に必須)
- answer capture:
  - `hard cutover` を採用する。不要な interface / field は削除する。
- 回答:
  - Option A: hard cutover。
  - `guidance issue-execution` の default Markdown / JSON / runbook projection から `selected_step`、`step_assurance`、`context_packets` を互換期間なしで削除する方針を採用する。
  - 旧 dynamic model の不要な interface / field は deprecated として残さず、要件・設計・実装計画で削除対象に含める。
- 回答日時:
  - 2026-06-27

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが hard cutover を明示的に採用したため。
  - 今回の目的は旧 dynamic guidance fields の互換維持ではなく、agent-facing authority を `plan.md` に一本化し、stale projection / multi-authority の再発を防ぐことにある。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - default `guidance issue-execution` は `selected_step`、`step_assurance`、`context_packets` を返してはならない。
  - 旧 dynamic model の interface / field は互換維持対象外とし、不要なものは削除する。
  - `plan.md` が実行順、worker、reviewer、verification、closure、commit/no-op、amendment trigger の authority であることを受け入れ条件に含める。
- `design.md`:
  - Runbook schema / presentation / projection から旧 dynamic fields を削除する。
  - `workflow_next()` の default issue-execution path から step assurance / context packet compile を削除する。
  - `context_packets.py` / `context_routing.py` / related stores / tests は削除または未使用化ではなく、不要 interface として削除する方向で設計する。ただし残存利用がある場合は provider source 上で確認し、削除範囲を根拠付きで決める。
- `plan.md`:
  - runtime output contract 変更、旧 interface 削除、tests 置換、skill 文面更新、dogfooding validation を明示 step として扱う。
- `ADR`:
  - 不要。
- reflected_to 更新方針:
  - 要件定義・設計・計画の作成時に `reflected_to` を更新する。
- adoption reflection:
  - `hard cutover` はユーザー承認済みの仕様前提として扱う。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
