---
種別: ADR（Architecture Decision Record）
ID: "20260716t123423z-08-adr"
タイトル: "最小永続状態とWorkbench・report.mdのauthority境界"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
authority: "accepted"
derived_from:
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-026"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-027"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-069"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-070"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-071"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md#D2-072"
reflected_to:
  - "design.md"
  - "plan.md"
---

# 20260716t123423z-08-adr 最小永続状態とWorkbench・report.mdのauthority境界

## 位置づけ

このADRは、Git、GitHub、Oracle session、Workbench、Repair Batch、Executor Handoff、`report.md`の保存責務を分離し、vNextで新しいWorkflow databaseを作らない方針を固定する。

## ADR 化基準

- hard to reverse:
  - yes。receipt、registry、parser、state fileの有無はRuntimeと全Workflowへ波及する。
- surprising without context:
  - yes。長時間Workflowであっても、Review BASEやrepair iterationの専用stateを作らない。
- real tradeoff:
  - yes。完全な再開性より、重複状態とstale管理を避け、必要時に広いReviewを再実行する方を選ぶ。
- ADR として残す理由:
  - 将来の機能追加でstate fileを安易に再導入することを防ぐため。

## 結論（Decision）

- `requirement.md`、`design.md`、`plan.md`、Git history、GitHub PR／CI、Oracle sessionを既存authority surfaceとして利用する。
- Review receipt、Planning state、accepted HEAD registry、Checkpoint state、Repair iteration DB、custom Git refs、Plan parser、Review JSON parserを新設しない。
- BASEやcontextを失った場合はGit／Oracleから復元し、確定できなければより古い安全なBASEでfresh Reviewする。
- Workbenchはroot／Scope内のGit非管理一時領域として、prompt、Operator Context、Blocking Intake、候補file、外部資料、長い診断へ利用する。
- Workbenchをcanonical authority、lifecycle state、Review receiptにはしない。
- Oracle sessionのprompt／response／log／artifactsをChatGPT実行記録の正本とする。
- Repair Batchはfrozen repair contractでありWorkflow stateではない。
- Executor Handoffは自由Markdownで返し、専用execution recordを作らない。
- `report.md`は巨大Evidence Ledgerではなく、Final Completion Summary、主要verification、主要repair、残存risk、次Actorへのhandoffを記録する。
- Current Effective Decision Snapshotは現在有効な判断だけを保持し、履歴を別audit surfaceへ分離する。

## 背景（Context）

既存Workflowでは、GitHubやOracleに存在する情報をreceipt、Evidence Ledger、repair iterationへ複製していた。これらは再開性を高める一方、更新忘れ、stale判定、Review後のstate-only commit、Runtime parserを増やす。

## 選択肢（Options considered）

### Option A: 専用stateを最小化し、既存surfaceから再構成する

- Pros:
  - 実装と保守が単純。
  - stale stateと二重authorityを避けられる。
  - 外部tool変更へ追従しやすい。
- Cons:
  - context喪失時に重複Reviewや再調査が必要。
- Decision:
  - Accepted.

### Option B: Workbenchへ標準state fileを置く

- Pros:
  - セッション再開が容易。
- Cons:
  - 非canonical fileが事実上のauthorityになりやすい。
- Decision:
  - Rejected as standard path.

### Option C: Git管理receipt／registryを作る

- Pros:
  - 高い耐久性。
- Cons:
  - Review済みHEAD後のstate-only commit、parser、migrationが必要。
- Decision:
  - Rejected.

## 判断理由（Rationale）

SpecDockの価値はstate machineの精密化ではなく、変更しやすいWorkflowと明確なauthorityにある。稀なcontext喪失時だけ再Reviewコストを払い、通常経路を単純に保つ方が総コストが低い。

## 影響（Consequences）

- Positive:
  - RuntimeとWorkflow文書が小さくなる。
  - Git／GitHub／Oracleの既存記録を直接利用できる。
  - model／Prompt変更でstate migrationが不要。
- Negative / debt:
  - exact BASEを失った場合は広いReviewが必要。
  - report.mdだけで全履歴を再現できない。
- Migration:
  - Evidence Ledger、review receipt、repair iteration等のmaintained必須surfaceを除去する。
  - Workbenchを一時用途へ限定するguidanceを更新する。
- Rollback:
  - 実測で再開コストが支配的になった場合、非canonical補助メモから段階的に再検討する。

## 参考（References）

- `design.md#11-reportmd-Workbench-永続状態`
- `plan.md#Epic-6`
