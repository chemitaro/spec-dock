---
種別: interview
ID: "20260716t235120z-02-interview-integrated-planning-and-document-authority"
タイトル: "Integrated Planning Bundleと文書Authority"
状態: "answered"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
  - "artifacts/20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md"
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
  - "artifacts/20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md"
---

# 20260716t235120z-02-interview-integrated-planning-and-document-authority Integrated Planning Bundleと文書Authority

## 位置づけ

- このArtifactは、長時間インタビューで確定した一つの本質的判断を、現在有効な状態へ正規化した回答済みInterview recordである。
- 過去の逐次会話や途中で上書きされた案を運用規則として残さず、最終回答、比較した代替、採用理由、canonical文書への含意だけを残す。
- 本文は生ログや非公開の内部推論ではなく、会話上で提示・比較・承認された判断材料の説明可能な要約である。

## 正式質問として扱う理由

- 影響するartifact:
  - `requirement.md`／`design.md`／`plan.md`:
    - 生成単位、authority、正本化
  - Planning Skill:
    - 生成、Review、Revision、Human decomposition gate
  - `spec-dock-chatgpt`:
    - `planning create`／`planning revise`
  - `ADR`:
    - Integrated Planning Bundleと`plan.md` SSOT
- chat上の軽微な一問では足りない理由:
  - 全ScopeのPlanning completion interfaceとcanonical authoring authorityを決めるため。

## 質問の目的

- 対象者:
  - Initiativeの意思決定者である人間ユーザー。
- 何を明確にする質問か:
  - Integrated Planning Bundle、complete-file output、direct placement、self-review、P0／P1 gate、Node materializationを固定すること。
- 回答が後続判断へ与える影響:
  - Requirement、Design、Initiative Plan、ADR、Epic boundary、Skill／Agent／CLIの具体化に直接影響する。

## 質問

- pressure-test question:
  - Initiative／Epic／Issueの三文書を、誰がどの単位で生成し、どのReview／Revision loopを通してcanonical化するか。
- 質問:
  - Initiative／Epic／Issueの三文書を、誰がどの単位で生成し、どのReview／Revision loopを通してcanonical化するか。
- 回答してほしいこと:
  - 採用する原則。
  - 棄却する代替。
  - Scope、authority、停止条件。
  - 後続Planningへ委譲する詳細。

## source-grounded context

- 確認済みのdocs／code／tests／ADR／discussions／primary source:
  - 現行Initiative／Epic／Issue Planning Skill
  - 旧`spec-dock-chatgpt-authoring`、Evidence Adoption Ledger、manual planning Skill
  - 現行Initiative／Epic／Issue template
- local contextで解決できたこと:
  - 三文書は相互依存が強く、phase別生成では整合性修正が増える
  - Node関係はmetadataにありIdentifyヘッダーを複製する必要はない
  - `plan.md`は人間とLLMの双方が読めるため別JSONは不要
- まだ人間判断が必要だった理由:
  - ChatGPT生成物を候補とみなすか、完全なcanonical fileとして使うかはauthorityの選択だから。

## 回答案

- Option A: Phase別authoring:
  - Requirement、Design、Planを順番に作り各phaseでReviewする。
- Option B: ChatGPT evidence＋Codex rewrite:
  - ChatGPT出力をclaim単位で採用しCodexがcanonical三文書を書き直す。
- Option C: Integrated Planning Bundle:
  - ChatGPTが三文書を一つのfresh sessionで生成・セルフレビューしCodexは内容不変で配置する。

## Codexの分析

- 判断軸:
  - 三文書整合性
  - authority
  - Reviewコスト
  - モデル能力活用
  - 変更容易性
- tradeoff:
  - Phase別は局所gateを持てるが同一論点を複数phaseで往復しやすい
  - Codex rewriteは二重authoringとなりChatGPTの統合設計を壊し得る
  - Integrated Bundleは一発目の品質とPlanning Skillの外部interfaceを単純化する
- リスク:
  - 初回生成にself-reviewがないと独立Review後の修正loopが増える
  - P2／P3まで修正するとReviewが収束しない
  - Node作成後に親Bundleを書き換えるとReview freshnessが失われる
- 具体シナリオ／edge case:
  - P0／P1はcomplete bundle revision後にfresh Planning Review
  - P2／P3のみならPASSし文書を変更しない
  - Human分割承認後に子Nodeを作り、親Bundleを変えなければ再Reviewしない

## Codexの推奨案

- 推奨:
  - Option C: Integrated Planning Bundle
- 理由:
  - GPT-5.6 Proの統合Planning能力を最大限利用できる
  - Codexによる二重authoringをなくせる
  - Planning完了時に整合済み三文書があるという単純なinterfaceになる
- 未回答時の影響:
  - Planning Skill、Prompt、Review、canonical placement、Node materializationが確定しない。

## ユーザー回答

- answer capture:
  - 三文書は一つの依頼・一つのsession・一つのBundleで生成する
  - ChatGPTが完全ファイルを作成しCodexは意味内容を再編集しない
  - `plan.md`を人間・LLM共通SSOTとする
- 回答:
  - Option Cを採用
  - 初回生成へadversarial self-reviewを含める
  - Lite以外はfresh independent Planning Reviewを行う
  - P0／P1のみblocking、P2／P3のみならPASS
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
  - Integrated Bundle、self-review、P0／P1 gateを必須能力化
- `design.md`:
  - complete-file output、direct copy、fresh review、Node materialization境界
- `plan.md`:
  - Planning cutoverを独立Epicへ割り当て
- `ADR`:
  - Integrated Planning Bundleと`plan.md` SSOTを固定

## 条件付き補足

- 後続reflection proposal:
  - canonical三文書またはaccepted ADRと矛盾する場合は、Interviewを直接実行authorityにせず、Planningで整合させる。
- 追加で作るdiscussion docs:
  - 複数Interviewを横断したrationaleは同梱の`disc-*`へ整理する。
