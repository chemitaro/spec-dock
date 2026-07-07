---
種別: interview
ID: "20260707t144547z-interview"
タイトル: "Human approval checkpoint for batch planning workflow"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "epic-00295"
created_at: "2026-07-07THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260707t143000z-interview-workflow-first-chatgpt-authoring-redesign-interview-1.md"
reflected_to:
  - "report.md#Evidence Adoption Ledger"
---

# 20260707t144547z-interview Human approval checkpoint for batch planning workflow

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
    - Human approval checkpoint と automation boundary。
  - `design.md`:
    - Batch planning workflow の承認状態遷移、Issue node 作成前 gate、draft adoption の自動化境界。
  - `plan.md`:
    - 実装順、skill / runtime command に必要な approval / automation contract。
  - `ADR`:
    - 将来、human approval policy を長期 decision として固定する場合の候補。
- chat 上の軽微な一問では足りない理由:
  - 人間承認 checkpoint の位置は、workflow の自動化範囲、runtime command の stop condition、skill の handoff 条件を決定する。

## 質問の目的 (必須)
- 対象者:
  - SpecDock の主利用者 / product owner。
- 何を明確にする質問か:
  - A -> B workflow において、人間の明示承認を必須にする checkpoint と、自動化する checkpoint。
- 回答が後続判断へ与える影響:
  - Issue node 作成前 gate、Issue draft adoption の自動化、Epic requirement 作成の entry mode が決まる。

## 質問 (必須)
- pressure-test question:
  - A -> B の一連 workflow で、人間の明示承認 checkpoint はどこに置くべきか。
- 質問:
  - Initiative / Epic から生成された Epic / Issue 分解案を node 作成する前と、各 Issue draft pack を canonical docs へ採用する前のどちらに人間承認を置くか。
- 回答してほしいこと:
  - 明示承認が必要な地点と、自動化したい地点。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - `workflow_epic.md`: Epic handoff package と Issue-local draft は planning evidence であり、Issue canonical docs ではない。
  - `spec-dock-epic-execution`: draft-only / unreviewed Issue docs は Issue Planning へ route する。
  - `spec-dock-issue-planning`: drafts are evidence, canonical docs require adoption and fresh reviewer gate.
  - `artifacts/20260707t143000z-interview-workflow-first-chatgpt-authoring-redesign-interview-1.md`: Option A primary, B downstream set。
- local context で解決できたこと:
  - A -> B の一連 workflow が主軸である。
  - Issue draft adoption は execution-ready ではなく、Issue Planning の正本化 step である。
- まだ人間判断が必要な理由:
  - どの段階で human approval を必須にするかは product workflow の体験設計であり、repo だけでは決められない。

## 回答案 (必須)
- Option A:
  - Issue node 作成前の分解案承認だけを人間 checkpoint にする。
  - Issue draft -> canonical docs の採用は自動化する。
- Option B:
  - Issue node 作成前と、各 Issue draft adoption 前の両方に人間承認を置く。
- Option C:
  - 人間承認は最小化し、Issue node 作成も draft adoption も自動化する。

## Codex の分析 (必須)
- 判断軸:
  - 人間の判断が本質的に必要な地点と、AI / runtime が安全に自動化できる地点の分離。
- tradeoff:
  - Issue node 作成前は、scope / slicing / 実装単位の妥当性を人間が確認する価値が高い。
  - Issue draft adoption 前にも人間承認を置くと安全だが、A -> B の連続 workflow が重くなり、ChatGPT batch planning の効率が落ちる。
  - Issue node 作成前の分解案を人間が確認済みであれば、各 Issue の正本化は自動化しやすい。
- リスク:
  - draft adoption を自動化する場合、unsafe claim、stale draft、profile mismatch、reviewer pass self-claim を runtime / skill / reviewer gate で必ず防ぐ必要がある。
- 具体シナリオ / edge case:
  - Epic Planning が Issue 10 件の draft pack を生成し、人間が Issue 分解案を承認する。その後 Epic Execution は各 Issue を start し、draft-adoption Issue Planning を自動で進める。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - 人間が本当に判断すべきなのは、Issue slicing / node 作成前の scope decision である。
  - ここで承認済みなら、下流の Issue draft adoption は automation target にできる。
- 未回答時の影響:
  - runtime command がどこで stop し、どこで自動続行するか決められない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A を採用する。
  - Epic 単位で具体化し、Issue 分解案を作成した後、実際に Issue を作成する前が人間の明示承認 checkpoint。
  - Issue draft pack を canonical docs へ整える地点は自動化する。
  - draft 案はすでに人間が確認している前提なので、各 Issue の正本化では人間承認を挟まない。
  - Epic requirement の作成は ChatGPT に依頼する場合も、人間と Codex が練って作る場合もある。
  - Epic requirement を人間と Codex で固めた後、その requirement に沿って Epic design / plan、Issue slicing、各 Issue draft を ChatGPT に依頼する case もある。
- 回答:
  - Issue node 作成前は human approval 必須。Issue draft adoption は自動化。
- 回答日時:
  - 2026-07-07

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Epic requirement を ChatGPT で作る case と、人間/Codex で固める case を同じ command / skill mode にするか、別 entrypoint にするか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - human approval checkpoint と automation boundary を決める product workflow decision であり、Epic の requirement / design / plan に反映する必要がある。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Issue 作成前の分解案承認を明示的 human checkpoint とする。
  - Issue draft adoption は自動化対象とする。
  - Epic requirement 作成には ChatGPT-generated path と human/Codex-authored path の両方がある。
- `design.md`:
  - Batch planning workflow は `Epic requirement source -> ChatGPT design/plan/Issue drafts -> human approval before Issue creation -> automated draft-adoption Issue Planning` を主軸にする。
  - approval state と draft adoption automation state を分離する。
- `plan.md`:
  - human approval gate と automated draft adoption validator / reviewer gate を別 Issue として扱う可能性が高い。
- `ADR`:
  - human approval checkpoint policy を長期 contract にする場合は ADR 候補。
- reflected_to 更新方針:
  - まず `report.md` EAL に反映し、requirement / design / plan 具体化時に採用する。
- adoption reflection:
  - `report.md` EAL に採用記録を追加する。

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
