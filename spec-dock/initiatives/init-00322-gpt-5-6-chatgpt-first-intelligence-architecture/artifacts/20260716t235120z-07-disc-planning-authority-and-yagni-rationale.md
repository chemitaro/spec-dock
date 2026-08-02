---
種別: disc
ID: "20260716t235120z-07-disc-planning-authority-and-yagni-rationale"
タイトル: "Planning AuthorityとYAGNIに基づく簡素化のDecision Rationale"
状態: "proposed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t123423z-01-adr-delegation-first-responsibility-boundary.md"
  - "artifacts/20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md"
  - "artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md"
authority: "synthesized"
derived_from:
  - "artifacts/20260716t235120z-01-interview-initiative-goal-authority-and-simplification.md"
  - "artifacts/20260716t235120z-02-interview-integrated-planning-and-document-authority.md"
  - "artifacts/20260716t131924z-01-research-initiative-bootstrap-repository-baseline.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
---

# 20260716t235120z-07-disc-planning-authority-and-yagni-rationale Planning AuthorityとYAGNIに基づく簡素化のDecision Rationale

## 位置づけ

- この文書は、複数Interview・Research・ADRを横断し、採用判断へ至った説明可能なrationale、tradeoff、設計含意を整理する。
- Current Effective Decision Snapshotとaccepted ADRを上書きしない。本文は決定に至った論点構造を後続Agentへ伝えるevidence surfaceである。
- 生ログや非公開の内部chain-of-thoughtを再現せず、会話上で明示された分析、比較、反証、ユーザー承認だけを要約する。

## 対象論点

- ChatGPTが三文書をcomplete fileとして一括生成するauthority
- Codexが意味内容を再執筆しない境界
- Identify、`plan.json`、receipt、Evidence Adoption Ledger、manual fallbackの廃止
- GitHubをtracked contentのSSOTとし、自動添付を行わない方針
- Workbenchを一時領域に限定する方針
- このsynthesisが必要な理由:
  - 個々の削除判断は同じ根本原則から導かれており、別々に読むと単なる機能削減に見える。後続Agentが旧機能を再導入しないため、共通rationaleをまとめる必要がある。

## derived question sheets／research

- `interview`／`research`:
  - artifacts/20260716t235120z-01-interview-initiative-goal-authority-and-simplification.md
  - artifacts/20260716t235120z-02-interview-integrated-planning-and-document-authority.md
  - artifacts/20260716t131924z-01-research-initiative-bootstrap-repository-baseline.md
- Current decision:
  - `artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md`
- Related ADR:
  - artifacts/20260716t123423z-01-adr-delegation-first-responsibility-boundary.md
  - artifacts/20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md
  - artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md

## synthesis

- 合意済みのこと:
  - PlanningはInitiative／Epic／Issueごとに公開Skillを持つが、共通mechanicsは共有文書へ集約する
  - 三文書は一つのfresh ChatGPT sessionで生成・セルフレビューする
  - ChatGPT出力はevidence fragmentではなくcomplete canonical candidateである
  - Codexはfile識別、配置、Git、Review orchestrationを担い、内容を再編集しない
  - `plan.md`を人間・LLM共通SSOTとし、別の機械用Plan stateを作らない
  - 不要なmetadataの正確性を管理するより、そのmetadataを削除する
- 未合意／未確定のこと:
  - Prompt本文、few-shot、Protocol別output artifact naming
  - Oracle output variationに対する最小file discovery手順
  - exact provider／installed asset path
- source-groundedに解決できたこと:
  - 現行三Planning Skillは旧ChatGPT evidence laneとmanual fallbackへ依存している
  - 既存Initiativeのcanonical三文書形式はvNextでも維持でき、document migrationは不要
  - Workbenchは既にmainへ導入済みで、候補やcontextの一時保管に利用できる

## 選択肢／tradeoff

- Option A: Runtime／Codexが細かく合成・検証:
  - Pros:
    - field単位で決定的に見える
    - 既存旧Workflowの延長で実装できる
  - Cons:
    - モデル変更時の改修面が広い
    - 二重authoringと二重stateが残る
    - 不要fieldのhallucination圧力を生む
  - Disposition:
    - Rejected
- Option B: ChatGPT complete bundle＋薄いorchestration:
  - Pros:
    - 統合推論を活用できる
    - authorityが一意
    - Workflowが短い
    - 変更容易性が高い
  - Cons:
    - output discoveryとlive smokeが必要
    - モデル品質へ依存する
  - Disposition:
    - Accepted
- Option C: 自由対話だけでPlanning:
  - Pros:
    - 最小実装
  - Cons:
    - 再現可能なoutput contractとcanonical placementがない
    - Formal Reviewへ接続できない
  - Disposition:
    - Rejected

## reflection proposal

- canonical docs／workflow／template／skill guidanceへ反映すべき候補:
  - `workflow_planning.md`に共通spineだけを記載する
  - `workflow_chatgpt_delegation.md`にGitHub／Oracle／Operator Context境界を記載する
  - Planning Skillから旧authoring Skill、manual fallback、claim adoptionを削除する
  - templateからIdentify等の不要情報を除去する
- まだproposalに留める理由:
  - exact file path、Prompt本文、JSON field、Oracle config key等は各Epic Planningとlive smokeで決めるため。
  - 本文は実装authorityではなく、canonical文書とADRの解釈を助ける。

## adoption target／採用先候補

- `requirement.md`:
  - REQ-001〜REQ-010、NFR-001／004／005、Non-goals
- `design.md`:
  - Authority hierarchy、SSOT、Integrated Planning、Workbench
- `plan.md`:
  - Epic 1、Epic 2、Epic 6、Epic 7
- `ADR`:
  - Delegation responsibility、Integrated Planning、minimal state、global cutover
- `report.md`:
  - 最終成果と主要Revisionのみ。raw adoption ledgerは作らない

## ADR triage

- ADR candidateか:
  - yes
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADRとして残す理由:
  - Actor authority、SSOT、Review gate、Repair／Delivery境界、cutoverは将来のSkill／Runtime変更で再び誤って戻されやすいため。
- 対応するaccepted ADR:
  - artifacts/20260716t123423z-01-adr-delegation-first-responsibility-boundary.md
  - artifacts/20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md
  - artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md

## 推奨案

- 現時点の推奨案:
  - complete-file Integrated PlanningとYAGNIを共通原則とし、旧Evidence Laneを全面撤去する。
- 理由:
  - Current Effective Decision Snapshot、canonical三文書、accepted ADRが同じ方向を示しており、旧案を再導入する根拠がない。

## 推奨反映先

- `requirement.md`:
  - REQ-001〜REQ-010、NFR-001／004／005、Non-goals
- `design.md`:
  - Authority hierarchy、SSOT、Integrated Planning、Workbench
- `plan.md`:
  - Epic 1、Epic 2、Epic 6、Epic 7
- `ADR`:
  - Delegation responsibility、Integrated Planning、minimal state、global cutover
- `report.md`:
  - 最終成果と主要Revisionのみ。raw adoption ledgerは作らない

## 未採用／deferred理由

- 未採用:
  - Codexによるcanonical三文書の再執筆
  - phaseごとの個別authoring／review
  - `plan.json`、Planning receipt、Review recipe、Identifyヘッダー
  - Oracle障害時の旧manual planning Skill
- deferred:
  - 正確なPrompt wordingとOracle artifact discoveryはEpic 1／2のsmoke後に確定
  - 旧historical Scopeの文書修正は行わない

## 次アクション

- Epic 1で現行asset inventoryと`spec-dock-chatgpt`境界を確定する
- Epic 2で三Planning Skillとtemplate／workflow docsを全面改訂する
- Planning-only commitとfresh Planning Reviewをdogfoodする
- 追加で作るdiscussion docs:
  - なし。本pack内のInterview、Research、Decision Snapshot、ADR、self-reviewで必要な説明面を構成する。
