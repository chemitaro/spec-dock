---
種別: interview
ID: "20260713t012046z-interview"
タイトル: "Mandatory ChatGPT Consultation Scope"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
関連: []
scope: "issue"
scope_id: "iss-00313"
created_at: "2026-07-13T01:20:46Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md"
reflected_to:
  - "20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md"
  - "requirement.md authoring input"
  - "design.md authoring input"
  - "plan.md authoring input"
  - "report.md Evidence Adoption Ledger"
---

# 20260713t012046z-interview Mandatory ChatGPT Consultation Scope

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / artifacts / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `blank` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Mandatory ChatGPT-Use consultationが適用されるreview outcomeを確定する。
  - `design.md`:
    - Clean/non-blocking terminal pathがexternal browser availabilityへ依存するかを決める。
  - `plan.md`:
    - Manual scenarioとfailure gateの対象範囲を決める。
  - `ADR`:
    - External consultation gateの適用境界としてADR candidate triageへ影響する。
- chat 上の軽微な一問では足りない理由:
  - 回答によりnormal terminal workflow、availability、cost、human gate条件が変わる。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / PR delivery workflow owner。
- 何を明確にする質問か:
  - Completed reviewのどの分類でChatGPT-Useを必須にするか。
- 回答が後続判断へ与える影響:
  - Skill sequence、consultation failure gate、repair-batch creation条件を確定する。

## 質問 (必須)
- pressure-test question:
  - Findingがないclean reviewや明白なP2/P3-onlyでもChatGPT consultationを必須にすると、追加分析価値がない一方でbrowser障害によりmerge-prepared到達を止めないか。
- 質問:
  - ChatGPT-Use consultationは、completed reviewのうち`blocking_repair_required`またはblocker validity/scopeが不明なケースだけ必須にし、`merge_prepared_clean`と明白な`terminal_non_blocking_only`では省略する方針でよいですか。
- 回答してほしいこと:
  - Option A / B / Cの選択、またはmandatory範囲の修正。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Current merge-preparer skill、blocker-centric ADR、product-owner raw proposal、ChatGPT consultation result。
- local context で解決できたこと:
  - Blocking repairではChatGPT-Useを必須にし、integrated repair-batch body candidateを作成する。
- まだ人間判断が必要な理由:
  - ユーザーの「レビューが完了したら」は全outcomeともblocking repair時とも読め、clean pathのavailability/costをどこまで受け入れるかはproduct-owner判断だから。

## 回答案 (必須)
- Option A:
  - **Blocking/uncertainのみ必須（推奨）**。Cleanと明白なP2/P3-onlyはconsultation/batchなしでterminal handlingする。
- Option B:
  - **全completed reviewで必須**。Finding zeroやP2/P3-onlyもChatGPT分析を通し、成功しなければ停止する。
- Option C:
  - **Findingありで必須**。P0-P3のいずれかがあれば分析するが、cleanだけ省略する。

## Codex の分析 (必須)
- 判断軸:
  - Infinite repair防止への寄与、clean path availability、外部依存、分析cost、P2/P3 terminal policy維持。
- tradeoff:
  - Aはrepair判断に分析を集中し、clean pathを外部障害から守る。Bは一貫するが、価値のない分析でterminal PRを止めうる。Cはnon-blocking findingの再分析がbranch mutation禁止と混線しやすい。
- リスク:
  - Aではcoarse routingをorchestratorが正しく行う必要がある。B/CではChatGPT failureが新しい不要停止になる。
- 具体シナリオ / edge case:
  - Review completionがno-findings、P2/P3-only、P1あり、priority不明の4ケース。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - ChatGPT分析の目的はblocking repairの統合分析とstagnation防止であり、修復不要なterminal pathまで外部gate化する必要はないため。
- 未回答時の影響:
  - Requirementとworkflow sequenceを確定できず、canonical authoringへ進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 2026-07-13のチャットで、ChatGPT raw分析レポート案全体を採用すると明示した。
- 回答:
  - Option Aを採用する。
  - ChatGPT-Use consultationは`blocking_repair_required`またはblocker validity/priority/scopeが不明なcompleted observationで必須にする。
  - `merge_prepared_clean`と明白な`terminal_non_blocking_only`ではconsultationとrepair batchを省略する。
  - Recovery不能なmandatory consultationはfail-closed human gateを既定とし、人間がinvocation単位で明示承認した場合だけ一回限りのmanual fallbackを許可する。
  - Legacy discussion repair-batch templatesはIssue #313でartifact templateと同じbody contractへ同期し、deprecation/removalは別Issueに委ねる。
- 回答日時:
  - 2026-07-13 Asia/Tokyo

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`, ADR candidate triage, `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Product ownerがraw ChatGPT分析レポート案を全面採用し、レポート内の推奨回答で全候補論点を確定したため。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Mandatory consultationの適用outcomeとfail-closed/manual waiver境界を固定する。
- `design.md`:
  - Clean/non-blocking terminal pathをexternal browser gateから分離し、blocking/uncertain pathにbody-candidate adoptionを置く。
- `plan.md`:
  - Blocking、uncertain、clean、P2/P3-only、recovery failure、manual waiver、legacy template parityを検証する。
- `ADR`:
  - Mandatory external consultationとintegrated batch authorityはdurable trust-boundary decisionとしてADR candidate triageする。
- reflected_to 更新方針:
  - Synthesisをcanonical authoringへ採用し、report EALにsourceと判断を記録する。
- adoption reflection:
  - ChatGPT raw transcriptの推奨案全体を採用し、要約researchはnavigation/synthesisとしてのみ使用する。

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
- 追加で作る artifacts:
  - ...
