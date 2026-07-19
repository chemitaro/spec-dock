---
種別: interview
ID: "20260716t235120z-04-interview-repair-batch-executor-and-git-boundaries"
タイトル: "Repair Batch・Executor・Git Transaction境界"
状態: "answered"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
  - "artifacts/20260716t123423z-05-adr-frozen-repair-batch-contract.md"
  - "artifacts/20260716t123423z-06-adr-main-executor-git-ownership.md"
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
  - "artifacts/20260716t123423z-05-adr-frozen-repair-batch-contract.md"
  - "artifacts/20260716t123423z-06-adr-main-executor-git-ownership.md"
---

# 20260716t235120z-04-interview-repair-batch-executor-and-git-boundaries Repair Batch・Executor・Git Transaction境界

## 位置づけ

- このArtifactは、長時間インタビューで確定した一つの本質的判断を、現在有効な状態へ正規化した回答済みInterview recordである。
- 過去の逐次会話や途中で上書きされた案を運用規則として残さず、最終回答、比較した代替、採用理由、canonical文書への含意だけを残す。
- 本文は生ログや非公開の内部推論ではなく、会話上で提示・比較・承認された判断材料の説明可能な要約である。

## 正式質問として扱う理由

- 影響するartifact:
  - `workflow_repair_batch.md`:
    - Blocking Intake、生成、採用、freeze、escalation
  - Issue Execution／PR Delivery:
    - repair routingとfresh Review
  - Executor config:
    - 裁量と停止条件
  - `ADR`:
    - Frozen Repair Batch、Main-owned Git
- chat上の軽微な一問では足りない理由:
  - Review修正の品質、Scope、永続化、Agent権限、Git transactionを横断して決めるため。

## 質問の目的

- 対象者:
  - Initiativeの意思決定者である人間ユーザー。
- 何を明確にする質問か:
  - Repair Batchの役割、ChatGPT／Main／Executor authority、freeze、commit／push所有者を固定すること。
- 回答が後続判断へ与える影響:
  - Requirement、Design、Initiative Plan、ADR、Epic boundary、Skill／Agent／CLIの具体化に直接影響する。

## 質問

- pressure-test question:
  - Approved PlanにないReview修正を、場当たり的patchや全面Replanningにせず、安全で実行可能な契約としてExecutorへ渡すにはどうするか。
- 質問:
  - Approved PlanにないReview修正を、場当たり的patchや全面Replanningにせず、安全で実行可能な契約としてExecutorへ渡すにはどうするか。
- 回答してほしいこと:
  - 採用する原則。
  - 棄却する代替。
  - Scope、authority、停止条件。
  - 後続Planningへ委譲する詳細。

## source-grounded context

- 確認済みのdocs／code／tests／ADR／discussions／primary source:
  - 現行`github-pr-merge-preparer`とPR #323のRepair Batch
  - 旧dev-coder／doc-writer／Reviewer構成
  - Codex agent loggerとWorkbench
- local contextで解決できたこと:
  - findingとCI evidenceはGitHub／Oracleへ分散し直接Executorへ渡すと統合が失われる
  - PR stateをRepair Batchへ複製すると巨大なworkflow databaseになる
  - Executorがcommit／pushするとMain確認前に外部gateを起動する
- まだ人間判断が必要だった理由:
  - どこまで文書化し、どのAgentへmutation権限を与えるかは運用上のtradeoffだから。

## 回答案

- Option A: Findingを直接Executorへ渡す:
  - 最小だが関連付けと修復設計がMain contextにしか残らない。
- Option B: 全修正をPlanning Revision:
  - canonical整合は強いが局所修正にも高コスト。
- Option C: Frozen Repair Batch:
  - ChatGPTがblocking setを分析し小規模な再設計・再計画を作りMainが採用してfreezeする。
- Option D: PR state ledgerとして更新:
  - 再開性は高いがstale情報と文書更新commitが増える。

## Codexの分析

- 判断軸:
  - root cause統合
  - Scope制御
  - 再開性
  - 二重状態
  - Executor効率
- tradeoff:
  - 直接委任は速いが非自明repairで誤修正しやすい
  - 全Replanningは安全だが軽微修正には重すぎる
  - Frozen Batchは上位Planへ従属するbounded contractになる
- リスク:
  - 実施結果をBatchへ追記すると計画と事実が混在する
  - 同一Batchを更新し続けると新旧HEADの問題が混ざる
  - ExecutorがGit操作を所有すると外部gate起動が早すぎる
- 具体シナリオ／edge case:
  - 同一Source HEADのP0／P1とCI failureを一つのblocking setにする
  - MainがChatGPT候補を採用／partial-use／棄却する
  - 採用後はfreezeし新HEADのblockerは新Batchにする
  - material変更が必要ならPlanningへ戻る

## Codexの推奨案

- 推奨:
  - Option C: Frozen Repair Batch
- 理由:
  - 小規模な再設計・再計画を永続化できる
  - workflow stateの二重管理を避けられる
  - Executorへ明確なallowed／forbidden scopeを渡せる
- 未回答時の影響:
  - Checkpoint／Delivery／PR repairの責務とAgent権限が確定しない。

## ユーザー回答

- answer capture:
  - Repair Batchはfinding群をfamily化し修復設計と実装計画をExecutorへ渡す
  - ChatGPT 5.6 Proが完全Markdownを生成する
  - 実施記録ではないため採用後はfreezeする
- 回答:
  - Option Cを採用
  - Checkpoint、Delivery、PR／CIへ共通利用
  - Executorは意味的契約内で柔軟に変更する
  - commit／pushはMainが所有
  - Executor handoffは薄いspineを持つ自由Markdown
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
  - accepted blockerに対するChatGPT Repair Batch生成
- `design.md`:
  - subordinate authority、freeze、Source HEAD binding、Git境界
- `plan.md`:
  - Repair Batch／Executor-centered executionを独立Epic化
- `ADR`:
  - Frozen Repair BatchとMain-owned Git transactionを固定

## 条件付き補足

- 後続reflection proposal:
  - canonical三文書またはaccepted ADRと矛盾する場合は、Interviewを直接実行authorityにせず、Planningで整合させる。
- 追加で作るdiscussion docs:
  - 複数Interviewを横断したrationaleは同梱の`disc-*`へ整理する。
