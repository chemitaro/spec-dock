---
種別: interview
ID: "20260803t011239z-interview"
タイトル: "iss-00354 継続スレッド失敗時の停止と再開規則"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-08-03"
親: ["iss-00354"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00354"
created_at: "2026-08-03THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260803t011239z-interview iss-00354 継続スレッド失敗時の停止と再開規則

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
    - 継続threadの利用不能・期限切れ・identity不一致・添付差分時の停止条件と、再開に必要な完全identity再提示の要件。
  - `design.md`:
    - thread handleの検証、source HEAD／Candidate identity／attachment manifestの再検証、fail-closedと新規thread再作成の境界。
  - `plan.md`:
    - continuity failureを検出する実装順、negative test、同一thread再利用とfresh thread作成の証跡、移行時の保守手順。
  - `ADR`:
    - Issueを越えて永続化するconversation identity／retention／復旧ポリシーに昇格する場合だけ候補化する。
- chat 上の軽微な一問では足りない理由:
  - 継続失敗時に自動送信を許すか停止するかは、誤ったrepository・branch・Candidateへの送信と、Human gate前の不正なauthoringを防ぐ安全境界を直接決めるため。

## 質問の目的 (必須)
- 対象者:
  - Issue owner（ユーザー）。
- 何を明確にする質問か:
  - Option Aで採用したBlue Team継続threadが利用できない場合に、どの条件で送信を停止し、どのように安全に再開するか。
- 回答が後続判断へ与える影響:
  - fail-closedの強さ、新規thread作成の自動性、完全context再送の必須性、Human confirmationの要否、および復旧証跡の必須項目が決まる。

## 質問 (必須)
- pressure-test question:
  - Option Aの継続範囲を保ったまま、古いthread文脈や誤ったidentityが再利用される事故を防げる停止条件になっているかを確認する。
- 質問:
  - Blue Teamの継続threadが利用不能・期限切れ・別repository／branchに結び付いている・source HEADやattachment manifestが不一致になっている場合、どの停止／再開規則を採用しますか？
- 回答してほしいこと:
  - **Option A（推奨）**: fail-closedで送信を停止する。自動で本文だけを送り直さず、同じthreadのidentityを再検証できる場合だけ再開する。継続不能なら、現在のrepository／branch／HEAD、thread lineage、必要な添付一式を完全に再提示した新規Blue threadを作成し、旧threadとの関係を記録してから再開する。identityが曖昧な場合は人間確認を要求する。
  - **Option B**: 継続失敗時は自動的に新規Blue threadを作成し、完全contextと添付一式を再送して継続する。identity不一致だけは停止する。
  - **Option C**: どの継続失敗でも自動再開せず、必ず人間確認を得てから新規thread作成または再送を行う。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Issue #354の調査artifact、前問の回答artifact、`issue_planning_chatgpt.py`、`issue_planning_prompt.py`、planner／reviewer／revision／transport resource、`workflow_clarification.md`、`workflow_chatgpt_authoring_pack.md`、focused tests。
- local context で解決できたこと:
  - 現行runtimeはphaseごとに新規sessionを作成し、同一invocation内だけstatus／harvestで回復する。exact repository／branch／HEAD、Candidate identity、添付のauthority、fresh Red Team Review、Human gateが既存契約として確認できる。
- まだ人間判断が必要な理由:
  - Oracleのconversation handle保持や添付更新能力だけでは、利用不能時の安全な業務運用（自動再開か人間確認か）を決められず、ユーザーのリスク許容度と責務境界の判断が必要だから。

## 回答案 (必須)
- Option A:
  - fail-closed。継続できない状態では送信せず、再検証可能なら同一threadで再開し、継続不能なら完全な現在contextを添付した新規Blue threadへ切り替える。identityが曖昧なら人間確認で停止する。
- Option B:
  - 自動で新規Blue threadを作成して完全contextを再送する。停止時間は短いが、意図しないthread分岐やidentity誤結合を自動で許す。
- Option C:
  - すべての継続失敗で人間確認を要求する。安全性は高いが、長時間処理の再開摩擦と運用負荷が最大になる。

## Codex の分析 (必須)
- 判断軸:
  - 誤送信防止、exact source identity、Candidate／Review immutable性、Blue／Red分離、Human gate、復旧の再現性、長時間ChatGPT運用の停止時間。
- tradeoff:
  - Aは誤ったidentityの自動継続を防ぎつつ、検証可能な場合の再開を許す。Bは復旧が速いが、thread lineageの誤りを自動で増やす。Cは最も保守的だが、明確なidentityを持つ一時的なtransport失敗まで人間待ちになる。
- リスク:
  - fail-closedの定義が曖昧だと、本文だけの無断再送、default branch fallback、古いCandidate添付の再利用、新規threadのsource HEAD欠落が起きる。
- 具体シナリオ / edge case:
  - source HEADだけが変わった場合、旧Blue threadを継続せず、変更理由と新HEADを含む再検証を要求する。
  - thread handleが失われた場合、旧threadへ再送を試みず、完全contextとattachment manifestを備えた新規Blue threadへ切り替える。
  - threadは利用可能だがrepository／branch identityが異なる場合、直ちに停止し、人間確認なしに再利用しない。
  - 添付アップロードが一部失敗した場合、本文だけの代替生成を禁止し、添付一式を再構成してから再開する。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。ただし新規Blue threadの自動作成は、identity・添付一式・旧thread lineageが機械的に確定できる場合に限定し、曖昧さが残る場合は人間確認で停止する。
- 理由:
  - Option Aは、ユーザーが承認したBlue継続／Red fresh分離と整合し、本文だけの不完全再送や誤ったrepositoryへの継続を防ぐ。完全context再送を要求することで、新threadでも判断根拠を復元できる。
- 未回答時の影響:
  - continuity failureの安全境界を確定できず、thread handleを実装へ追加する前に仕様を固定できない。canonical三文書のauthoringは継続して保留する。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 原文: 「オプションAを採用します。」
- 回答:
  - Option Aを採用する。検証済みの同一Blue threadだけを再開し、不一致・利用不能時はfail-closedで旧threadを正本扱いせず、完全なidentity/contextと添付一式を備えた新規Blue threadへ移行する。Candidate lineageなどが曖昧な場合は人間確認を要求する。
- 回答日時:
  - 2026-08-03（Codex会話上の回答時刻）

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes。各phaseで本文と添付に何を置き、どの資料を必須添付とするかを別の一問で確認する。
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Planner／Reviewer／Semantic Revision／Clarificationごとのcontext envelopeとattachment matrixの最小必須項目。

## 採用判断 (回答後に必須)
- adoption_status:
  - `adopted`（ユーザーがOption Aを明示承認）。
- adoption target:
  - Issue #354の`requirement.md`、`design.md`、`plan.md`、および`report.md`のEvidence Adoption Ledger（canonical authoring時に反映）。
- 採用 / 棄却 / deferred の理由:
  - ユーザーがOption Aを採用した。ChatGPT advisoryも、同一thread再開を検証済みに限定し、identity不一致時だけ新規threadへ完全contextを再送する方針を推奨しており、Blue／Red分離とHuman gateに整合する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - 継続threadのfail-closed条件、完全identity/context再送、新規Blue threadへの移行、曖昧時のHuman confirmationを反映する。
- `design.md`:
  - thread status、identity再検証、attachment manifest SHA、旧thread lineage、resume modeの保持と判定を反映する。
- `plan.md`:
  - 同一thread検証、完全context再送、新規thread移行、曖昧ケース停止、negative testの順序を反映する。
- `ADR`:
  - Issueを越えて永続化するconversation recovery policyへ昇格する場合のみ候補化する。現時点ではIssue-local方針として扱う。
- reflected_to 更新方針:
  - canonical三文書を作成する段階で、回答IDとChatGPT advisory artifactをEvidence Adoption Ledgerへ紐付ける。
- adoption reflection:
  - canonical三文書未作成のため`reflected_to: []`を維持する。

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
