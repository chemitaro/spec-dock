---
種別: disc
ID: "20260716t235120z-08-disc-review-architecture-decision-rationale"
タイトル: "Contract-Driven Review ArchitectureのDecision Rationale"
状態: "proposed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md"
authority: "synthesized"
derived_from:
  - "artifacts/20260716t235120z-03-interview-review-protocols-scope-and-perspectives.md"
  - "artifacts/20260716t235120z-11-research-openai-codex-review-target-and-scope-model.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
---

# 20260716t235120z-08-disc-review-architecture-decision-rationale Contract-Driven Review ArchitectureのDecision Rationale

## 位置づけ

- この文書は、複数Interview・Research・ADRを横断し、採用判断へ至った説明可能なrationale、tradeoff、設計含意を整理する。
- Current Effective Decision Snapshotとaccepted ADRを上書きしない。本文は決定に至った論点構造を後続Agentへ伝えるevidence surfaceである。
- 生ログや非公開の内部chain-of-thoughtを再現せず、会話上で明示された分析、比較、反証、ユーザー承認だけを要約する。

## 対象論点

- Formal ReviewとTargeted Reviewの分離
- Planning／Checkpoint／Delivery Protocol
- Delta-bounded Snapshot Review
- Meaningful BASE SHA、Mutation Frontier、Semantic Expansion
- Protocol固有JSON、P0／P1 gate、repository-conventions Perspective
- このsynthesisが必要な理由:
  - Reviewの個別fieldより、なぜ差分とsnapshotを組み合わせ、ProtocolとPerspectiveを分離したかを理解しないと、実装時に単純diff reviewやrepository全体監査へ戻りやすい。

## derived question sheets／research

- `interview`／`research`:
  - artifacts/20260716t235120z-03-interview-review-protocols-scope-and-perspectives.md
  - artifacts/20260716t235120z-11-research-openai-codex-review-target-and-scope-model.md
- Current decision:
  - `artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md`
- Related ADR:
  - artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md

## synthesis

- 合意済みのこと:
  - Formal ReviewはPlanning、Checkpoint、Deliveryの3 Protocol
  - Targeted Reviewは公開Skillを持つadvisory review
  - PlanningはHEAD snapshot、Checkpoint／Deliveryは意味的BASE..HEAD
  - BASE..HEADは対象選択、HEAD snapshotは契約充足判定に使う
  - pathはhard boundaryではなくStructural Anchor
  - P0／P1だけがblocking、P2／P3のみならPASS
  - 明示規約だけを`repository-conventions`で評価する
- 未合意／未確定のこと:
  - Protocol別JSONのexact field名
  - Perspective promptの最終catalogとdefault matrix
  - GitHub Connectorがexact branch／SHAを確認するlive挙動
- source-groundedに解決できたこと:
  - OpenAI CodexはUncommitted／BaseBranch／Commit／Customの小さなReviewTargetを持つ
  - BaseBranch reviewはmerge-baseから実際にmergeされる差分を対象にする
  - review-agentはcomplete diffを起点にcallers／tests等の最小supporting contextへ展開する
  - Hosted GitHub Codexの完全なserver実装は公開範囲で確認できない

## 選択肢／tradeoff

- Option A: 各Milestoneで固定フルReview:
  - Pros:
    - 手順が機械的
    - Review漏れが少ない
  - Cons:
    - 重複と待ち時間が大きい
    - Milestone意味を問わず同じReviewを実施する
  - Disposition:
    - Rejected
- Option B: Protocol＋Plan-driven Checkpoint:
  - Pros:
    - Contract Ownerと時間範囲が明確
    - 必要なCheckpointだけ置ける
    - Targeted Reviewを分離できる
  - Cons:
    - Planning品質が必要
    - BASE管理をMainが理解する必要がある
  - Disposition:
    - Accepted
- Option C: 現在HEADのrepository全体監査:
  - Pros:
    - BASEを持たなくてよい
  - Cons:
    - 変更起因性が失われる
    - 既存問題でnoiseが増える
    - Scopeが無制限
  - Disposition:
    - Rejected

## reflection proposal

- canonical docs／workflow／template／skill guidanceへ反映すべき候補:
  - `workflow_review.md`へReview scope model、freshness、Perspective、Result semanticsを一元化する
  - 各Workflow Ownerは起動条件と結果routingだけを持つ
  - `spec-dock-targeted-review`はformal gateを持たない
  - 旧local Reviewer Agentを削除し、GitHub Codex PR Reviewだけを外部channelとして残す
- まだproposalに留める理由:
  - exact file path、Prompt本文、JSON field、Oracle config key等は各Epic Planningとlive smokeで決めるため。
  - 本文は実装authorityではなく、canonical文書とADRの解釈を助ける。

## adoption target／採用先候補

- `requirement.md`:
  - REQ-011〜REQ-015、AC-005〜AC-007
- `design.md`:
  - Section 7 Review設計、Security／Reliability
- `plan.md`:
  - Epic 3、Epic 5、Epic 7
- `ADR`:
  - Contract-driven Review Protocol
- `report.md`:
  - 最新headの最終verdictと残存riskだけ

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
  - artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md

## 推奨案

- 現時点の推奨案:
  - Protocol-driven、delta-bounded snapshot、perspective-composed Reviewを採用し、Formal Gateとadvisory Targeted Reviewを分離する。
- 理由:
  - Current Effective Decision Snapshot、canonical三文書、accepted ADRが同じ方向を示しており、旧案を再導入する根拠がない。

## 推奨反映先

- `requirement.md`:
  - REQ-011〜REQ-015、AC-005〜AC-007
- `design.md`:
  - Section 7 Review設計、Security／Reliability
- `plan.md`:
  - Epic 3、Epic 5、Epic 7
- `ADR`:
  - Contract-driven Review Protocol
- `report.md`:
  - 最新headの最終verdictと残存riskだけ

## 未採用／deferred理由

- 未採用:
  - 旧Milestone Review名称
  - 全Gradeでの一律各Milestone Review
  - 全Protocol共通巨大JSON Envelope
  - Targeted Reviewの`pass/fail` formal semantics
  - Review BASE registry／tracked receipt
- deferred:
  - Perspectiveごとのfew-shotとexact JSON Schema
  - 二重Reviewの長期継続可否は実測後に判断

## 次アクション

- Epic 3でProtocol別prompt／JSON／Targeted Skillを実装する
- OpenAI Codex由来のreview target原則をtest caseへ落とす
- Epic 7でGitHub exact SHAとReview output安定性をlive smokeする
- 追加で作るdiscussion docs:
  - なし。本pack内のInterview、Research、Decision Snapshot、ADR、self-reviewで必要な説明面を構成する。
