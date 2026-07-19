---
種別: interview
ID: "20260719t135413z-01-interview"
タイトル: "Architecture-Aware Execution Brief — 現在有効な回答"
状態: "answered"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "user-approved evidence"
derived_from:
  - "ChatGPT interview through 2026-07-19"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "20260719t135413z-05-adr-architecture-aware-execution-brief-as-frozen-subordinate-contract.md"
---

# Architecture-Aware Execution Brief — 現在有効な回答

## 位置づけ

このInterviewは、各Execution Unitの実装開始前にChatGPTを用いて実装の目的、現在状態、関連Artifact、architecture、契約、テスト戦略、実装戦略を具体化する仕組みについて、現在有効なHuman回答だけを整理する。旧`Domain-Aware`案、差分パッケージ案、過去の中間案は実装authorityとして扱わない。

## Q1. なぜExecution Briefが必要か

### 回答

第一の目的は、ChatGPTの横断調査と高深度分析を活用し、Executorが実装を開始する前に、目的、現状、制約、architecture、関連判断、テスト戦略、実装順序を十分に具体化することである。これにより、実装品質、理解の正確さ、初回収束性、手戻りの少なさを向上させる。

第二の目的は、関連Artifact探索、repository構造理解、実装候補比較、テスト戦略設計等の高コストな認知処理を、余力のあるChatGPTへ移し、希少なCodex token、tool call、試行錯誤をrepository mutation、verification、Workflow制御へ集中させることである。

品質を悪化させる資源削減は成功とみなさない。分析品質と実装確度を第一目的、Codex認知資源の有効活用を第二目的とする。

## Q2. 特定のarchitectureや設計手法を前提にするか

### 回答

前提にしない。SpecDockは単純な変更、複雑な製品、独自framework、一般的framework、DDD、イベント駆動、CLI、build、deployment、documentation等の多様な作業へ利用される。

ChatGPTは、対象Execution Unitの正しい実装にmaterialなConcernをrepository evidenceから選択する。DDDやイベント駆動は関連する場合のAnalysis Lensであり、全Unitへ強制する固定templateではない。存在しないAggregate、Domain Event、Bounded Context、transaction semantics等を捏造してはならない。

## Q3. 関連Artifactを誰が選択するか

### 回答

Codexは意味的な関連Artifact選択を行わない。SpecDock／wrapperはrepository、branch、HEAD、Scope path、canonical document path、Artifact directory、dependency scope、Execution Unit ID等のdeterministic anchorだけを提示する。

ChatGPTがexact HEADを参照し、関連ADR、Interview、Discussion、Research、dependency report、code、tests、configuration、repository conventionsを横断的に探索・選択し、`Evidence Used`と`Evidence Gaps`をBriefへ記録する。

## Q4. Briefはどの粒度で作るか

### 回答

一つのcohesiveなExecution Unitにつき一つ作る。Issue Plan上のMilestoneまたはExecution Trancheを入力にできるが、file数ではなく、一つの目的、一つの主要な前提、一続きの検証戦略として実行できる意味的単位で扱う。

非機械的なUnitでは原則生成し、formatter、明白なrename、意味を変えない文書修正、一意なmirror同期等の機械作業では省略できる。

## Q5. Briefはどこへ保存し、どのauthorityを持つか

### 回答

`plan.md`をIssue全体のPlanning SSOTとして維持する。Execution BriefをIssue直下の第四canonical文書にはしない。

ChatGPT生成直後はWorkbench上のcandidateとし、Mainがbinding、status、evidence、scopeを確認した`ready`候補だけをIssue `artifacts/`へ内容不変で配置してfreezeする。accepted Briefは特定Execution Unitに限定されたfrozen subordinate execution contractであり、Requirement、accepted ADR、Design、Planを変更・上書きできない。

## Q6. Briefのstatusは何か

### 回答

- `ready`: exact HEAD、canonical contract、material Evidence、適用Concernを確認し、Plan内で実装可能。
- `planning-gap`: Requirement、Design、Plan、Scope、architecture、Review Topology等のmaterial変更が必要。Artifactへ昇格せずPlanningへ戻る。
- `insufficient-evidence`: exact HEAD、関連Artifact、contract、code、test seam等を確認できない。証拠を補うまで実装しない。

## Q7. ExecutorはBriefへどのように従うか

### 回答

ExecutorはBriefを主要入力として使うが盲信しない。Intended contractはRequirement、accepted ADR、Design、Plan、Observed stateはcurrent code、tests、configuration、Unit guidanceはaccepted Briefである。Plan内の局所差異はExecutorが調整しHandoffへ記録する。material conflictでは停止してPlanningへ戻る。

## Q8. Commitと更新の扱い

### 回答

accepted Briefは更新しない。Execution Briefだけの先行commitを標準にせず、対応する実装、tests、必要なdocs／configと同じcandidate commitへ含める。Source HEADやPlan等の前提がExecutor開始前にmaterialに変わった場合は新しいBriefを生成する。
