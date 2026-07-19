---
種別: interview
ID: "20260716t235120z-03-interview-review-protocols-scope-and-perspectives"
タイトル: "Review Protocol・Scope・Perspective・Result契約"
状態: "answered"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
  - "artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md"
scope: "initiative"
scope_id: "init-00322"
created_at: "2026-07-16T23:51:20Z"
created_by: "GPT-5.6 Pro"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "ChatGPTによるGrill Me／Grill with Docs形式の長時間インタビュー"
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md"
---

# 20260716t235120z-03-interview-review-protocols-scope-and-perspectives Review Protocol・Scope・Perspective・Result契約

## 位置づけ

- このArtifactは、長時間インタビューで確定した一つの本質的判断を、現在有効な状態へ正規化した回答済みInterview recordである。
- 過去の逐次会話や途中で上書きされた案を運用規則として残さず、最終回答、比較した代替、採用理由、canonical文書への含意だけを残す。
- 本文は生ログや非公開の内部推論ではなく、会話上で提示・比較・承認された判断材料の説明可能な要約である。

## 正式質問として扱う理由

- 影響するartifact:
  - Review Prompt／CLI:
    - Protocol、`--base-sha`、target、Perspective
  - Issue／Epic Plan:
    - Review TopologyとCheckpoint
  - Workflow Skill:
    - PASS／FAIL後のrouting
  - `ADR`:
    - Delta-bounded Snapshot Review
- chat上の軽微な一問では足りない理由:
  - Review timingとgate semanticsはPlanning、Execution、Delivery全体を支配するため。

## 質問の目的

- 対象者:
  - Initiativeの意思決定者である人間ユーザー。
- 何を明確にする質問か:
  - Planning／Checkpoint／Delivery／Targetedの境界、BASE／HEAD、Semantic Expansion、Perspective、Protocol固有JSONを固定すること。
- 回答が後続判断へ与える影響:
  - Requirement、Design、Initiative Plan、ADR、Epic boundary、Skill／Agent／CLIの具体化に直接影響する。

## 質問

- pressure-test question:
  - Reviewを重くしすぎず欠陥も逃さないため、Formal／Advisory ReviewをどのProtocol、Temporal Window、Perspective、Result契約で定義するか。
- 質問:
  - Reviewを重くしすぎず欠陥も逃さないため、Formal／Advisory ReviewをどのProtocol、Temporal Window、Perspective、Result契約で定義するか。
- 回答してほしいこと:
  - 採用する原則。
  - 棄却する代替。
  - Scope、authority、停止条件。
  - 後続Planningへ委譲する詳細。

## source-grounded context

- 確認済みのdocs／code／tests／ADR／discussions／primary source:
  - OpenAI Codexの`ReviewTarget`、merge-base review、review-agent
  - 現行SpecDockの`spec-reviewer`、`code-reviewer`、`qa-reviewer`
  - GitHub Codex PR Reviewの運用
- local contextで解決できたこと:
  - Codexは小さなtemporal targetをseedに必要なcallers／testsへ展開する
  - Checkpoint／Deliveryの意味的BASEはGit topologyだけでは自動決定できない
  - pathはhard boundaryではなくStructural Anchorとして使うべき
- まだ人間判断が必要だった理由:
  - Formal gateとadvisory reviewの区別、P2／P3の処理、Review頻度は運用価値判断だから。

## 回答案

- Option A: Grade別固定Review:
  - Strict以上は各Milestone、Lite／Standardは少数という機械規則。
- Option B: Planning時にReview Topologyを決めるProtocol方式:
  - Planning、Checkpoint、Deliveryを分離し必要なCheckpointだけPlanへ織り込む。
- Option C: 実装中にMainが都度判断:
  - 柔軟だがReview抜けと再現性低下が起きる。

## Codexの分析

- 判断軸:
  - 契約充足
  - 重複Review
  - freshness
  - Scope再現性
  - 変更見落とし
- tradeoff:
  - 固定Reviewは確実だが重い
  - 都度判断は柔軟だがReviewが抜ける
  - Plan-driven Topologyは理由を持ったCheckpointだけを置ける
- リスク:
  - diffだけではHEADの契約未達を見落とす
  - snapshotだけでは変更起因性を絞れない
  - pathをhard boundaryにするとcaller／consumer影響を見落とす
- 具体シナリオ／edge case:
  - Checkpoint／DeliveryはBASE..HEADをMutation FrontierとしHEADを契約へ照合
  - BASE不明時は古い安全なBASEへ広げる
  - Epic ReviewはIssue Reviewを再実行せずcross-Issue integrationを検証
  - 明示規約がなければ`repository-conventions`はN/A

## Codexの推奨案

- 推奨:
  - Option B: Planning時にReview Topologyを決めるProtocol方式
- 理由:
  - Review timingを事前に説明可能にする
  - ProtocolごとのContract OwnerとScopeを明確化する
  - 重複Reviewと見落としの双方を抑える
- 未回答時の影響:
  - Issue Plan、CLI、Review JSON、Repair routingが決められない。

## ユーザー回答

- answer capture:
  - Formal ReviewはPlanning、Checkpoint、Delivery
  - Targeted Reviewは対象とPerspectiveを指定するadvisory Skill
  - Checkpoint／DeliveryはDelta-bounded Snapshot Review
  - Perspectiveに`repository-conventions`を追加
- 回答:
  - Option Bを採用
  - Formal ReviewはProtocol固有JSON、P0／P1でFAIL、P2／P3のみでPASS
  - Targeted Reviewは`completed | insufficient_evidence`のadvisory JSON
  - ローカルReviewer Agentは削除しGitHub Codex PR Reviewは当面維持
- 回答日時:
  - 2026-07-16までのインタビューで逐次承認し、Current Effective Decision Snapshotへ統合。

## 追加確認の要否

- 追加確認が必要か:
  - no
- 必要な場合に次のunanswered `interview`として切り出す質問:
  - なし。field名、Prompt本文、正確なfile inventory等の実装詳細は各Epic Planningへ委譲する。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`、`design.md`、`plan.md`、accepted ADR
- 採用／棄却／deferredの理由:
  - 採用案がInitiative全体のauthorityとWorkflowを一貫させ、過剰なstate、二重authoring、暗黙分岐を避けるため。
- `report.md`への反映要否:
  - no。vNextの`report.md`はFinal Completion Summaryであり、このInterview全文を台帳へ転記しない。

## requirement／design／plan／ADRへの含意

- `requirement.md`:
  - Formal Protocol、Targeted Review、repository-conventions、P0／P1 gate
- `design.md`:
  - Contract Owner、Temporal Window、Structural Anchors、Mutation Frontier、Semantic Expansion
- `plan.md`:
  - Review Epicとlive smokeを独立配置
- `ADR`:
  - Delta-bounded Snapshot ReviewとProtocol固有JSONを固定

## 条件付き補足

- 後続reflection proposal:
  - canonical三文書またはaccepted ADRと矛盾する場合は、Interviewを直接実行authorityにせず、Planningで整合させる。
- 追加で作るdiscussion docs:
  - 複数Interviewを横断したrationaleは同梱の`disc-*`へ整理する。
