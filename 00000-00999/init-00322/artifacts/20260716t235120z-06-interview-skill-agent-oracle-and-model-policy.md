---
種別: interview
ID: "20260716t235120z-06-interview-skill-agent-oracle-and-model-policy"
タイトル: "Skill・Agent・Oracle・Model Policy"
状態: "answered"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
  - "artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md"
  - "artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md"
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
  - "artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md"
  - "artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md"
---

# 20260716t235120z-06-interview-skill-agent-oracle-and-model-policy Skill・Agent・Oracle・Model Policy

## 位置づけ

- このArtifactは、長時間インタビューで確定した一つの本質的判断を、現在有効な状態へ正規化した回答済みInterview recordである。
- 過去の逐次会話や途中で上書きされた案を運用規則として残さず、最終回答、比較した代替、採用理由、canonical文書への含意だけを残す。
- 本文は生ログや非公開の内部推論ではなく、会話上で提示・比較・承認された判断材料の説明可能な要約である。

## 正式質問として扱う理由

- 影響するartifact:
  - Skill／Agent inventory:
    - 維持、全面改訂、削除
  - `spec-dock-chatgpt`:
    - Oracle thin wrapperとGitHub binding
  - Agent config:
    - model／reasoning policy
  - Cutover Epic:
    - 全Scope workflow cutover、文書migrationなし
- chat上の軽微な一問では足りない理由:
  - 初期context、Codex quota、権限、fallback、provider／installed mirror保守を横断して決めるため。

## 質問の目的

- 対象者:
  - Initiativeの意思決定者である人間ユーザー。
- 何を明確にする質問か:
  - 残す／削除するSkill・Agent、Oracle wrapper、model／reasoning、global workflow cutoverを固定すること。
- 回答が後続判断へ与える影響:
  - Requirement、Design、Initiative Plan、ADR、Epic boundary、Skill／Agent／CLIの具体化に直接影響する。

## 質問

- pressure-test question:
  - 強いモデルを活用しながらSkill／Agentを増やしすぎず、Oracle変更やCodex default改善を妨げない最小トポロジーは何か。
- 質問:
  - 強いモデルを活用しながらSkill／Agentを増やしすぎず、Oracle変更やCodex default改善を妨げない最小トポロジーは何か。
- 回答してほしいこと:
  - 採用する原則。
  - 棄却する代替。
  - Scope、authority、停止条件。
  - 後続Planningへ委譲する詳細。

## source-grounded context

- 確認済みのdocs／code／tests／ADR／discussions／primary source:
  - 現行Planning Skill、manual Skill、`spec-dock-chatgpt-authoring`
  - local Reviewer、custom Explorer、Repository Analyst、doc-writer、worker
  - Oracle session／Browser Modeとローカル`chatgpt-use`
  - PR #323でmainへ導入済みのWorkbench
- local contextで解決できたこと:
  - Planning／Formal Review／Repair Batchは親Workflow内operationでCLIをさらにSkillでwrapする必要が薄い
  - Targeted Reviewはユーザーが直接依頼する独立目的を持つ
  - custom ExplorerはCodex built-in default改善を上書きする
- まだ人間判断が必要だった理由:
  - モデルコスト、Agent自由度、既存Scope cutoverは運用価値判断だから。

## 回答案

- Option A: 多数の専門Skill／Agentを維持:
  - 明示的だが初期contextとmirror更新が増える。
- Option B: 最小Skill／Agent＋共有docs＋CLI:
  - 親Workflowがoperationを所有し独立目的があるものだけSkill化する。
- Option C: 一つの汎用Skill／Agentへ統合:
  - 数は減るがmode分岐が巨大化する。

## Codexの分析

- 判断軸:
  - 独立ユーザー目的
  - 責務の閉じ方
  - 初期context
  - Codex defaultとの整合
  - 保守surface
- tradeoff:
  - 専門化しすぎるとroutingとmirror負債が増える
  - 統合しすぎると巨大Skillが多くのmodeを持つ
  - 公開Workflow Skill＋共有Reference＋CLIが中間となる
- リスク:
  - Custom ExplorerがCodex built-in改善を妨げる
  - Gradeとmodelを結合するとriskと認知難度が混同される
  - 旧Workflowを既存Scopeだけに残すと二重運用が長期化する
- 具体シナリオ／edge case:
  - Formal Review Skillなし、各WorkflowがCLIを直接呼ぶ
  - Targeted Reviewだけ公開Skill
  - Repair Batchは共有doc＋CLIで独立Skillなし
  - 既存Scope文書は変換せず次操作からglobal cutover

## Codexの推奨案

- 推奨:
  - Option B: 最小Skill／Agent＋共有docs＋CLI
- 理由:
  - 独立目的と内部operationを分離できる
  - Skill／Agent数とmirror負債を抑える
  - Codex defaultとOracle operator configを尊重する
- 未回答時の影響:
  - migration inventoryと削除／改訂範囲が確定しない。

## ユーザー回答

- answer capture:
  - Initiative／Epic／Issue Planning Skillは3つ維持
  - Formal Review Skillなし、Targeted Review Skillあり
  - Repair Batch Skillなし
  - custom Executor、built-in Explorer、Researcher、Consultant、Deep Consultantを残す
- 回答:
  - Option Bを採用
  - `spec-dock-chatgpt-authoring`、manual Planning Skill、local Reviewer、custom Explorer、Repository Analyst、Docs Writerを削除
  - Main／Executor／ExplorerはSpecDock側でmodel固定しない
  - ResearcherはLuna軽量、Consultant／Deep ConsultantはSolでreasoning差
  - 全ScopeのWorkflowを一括cutoverし文書migrationは行わない
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
  - Skill／Agent削減、Oracle thin adapter、global cutover
- `design.md`:
  - 公開Skill、共有Reference、CLI、Agent model policy
- `plan.md`:
  - Foundation、Planning、Review、Execution、Delivery、Cutover、Dogfood
- `ADR`:
  - Oracle境界とdocument migrationなしのcutoverを固定

## 条件付き補足

- 後続reflection proposal:
  - canonical三文書またはaccepted ADRと矛盾する場合は、Interviewを直接実行authorityにせず、Planningで整合させる。
- 追加で作るdiscussion docs:
  - 複数Interviewを横断したrationaleは同梱の`disc-*`へ整理する。
