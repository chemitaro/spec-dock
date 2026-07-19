---
種別: disc
ID: "20260716t235120z-14-disc-artifact-index-interview-discussion-research"
タイトル: "Initiative Planning Pack Artifact Index／Reading Guide"
状態: "proposed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
authority: "synthesized"
derived_from:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "artifacts/"
reflected_to:
  - "README.md"
---

# Initiative Planning Pack Artifact Index／Reading Guide

## 位置づけ

- この文書は、Planning Pack内のcanonical文書、Decision Snapshot、ADR、Interview、Discussion、Research、handoff、self-reviewを目的別に案内するindexである。
- Interviewはraw transcriptではなく、上書き後の最終回答へ正規化している。Discussionは説明可能なrationaleを残し、非公開の内部chain-of-thoughtを再現しない。
- authorityの優先順位は`initiative/design.md`のAuthority hierarchyに従う。Artifact間で矛盾がある場合、Human判断、canonical三文書、accepted ADR、frozen Repair Batchの順を優先する。

## 推奨Reading Order

1. `README.md` — 配置とdogfood手順。
2. `initiative/requirement.md` — 何を／なぜ行うか。
3. `initiative/design.md` — authority、SSOT、architecture、Workflow。
4. `initiative/plan.md` — 7 Epic、dependency、gate、rollout。
5. `artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md` — 現在有効なDecision Snapshot。
6. accepted ADR 9件 — durable decision。
7. Interview 6件 — 人間回答と個別tradeoff。
8. Discussion 4件 — 複数判断を横断したrationale。
9. Research 4件 — source-grounded facts、inference、未検証事項。
10. traceability、Epic materialization handoff、self-review。

## Artifact Catalog

| File | Type | Authority | Purpose |
|---|---|---|---|
| `20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md` | disc | `user-approved` | 現在有効なDecisionだけを統合した公式Discussion Snapshot。 |
| `20260716t123423z-01-adr-delegation-first-responsibility-boundary.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-04-adr-contract-driven-review-protocols.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-05-adr-frozen-repair-batch-contract.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-06-adr-main-executor-git-ownership.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md` | ADR（Architecture Decision Record） | `accepted` | accepted ADR: durable architecture／contract decision。 |
| `20260716t131924z-02-disc-initiative-requirement-design-epic-traceability.md` | disc | `synthesized` | Requirement／Design／Epic coverage matrix。 |
| `20260716t131924z-03-disc-integrated-planning-bundle-internal-self-review.md` | disc | `synthesized` | 初回Planning Bundleの内部セルフレビュー。 |
| `20260716t131924z-disc-epic-slice-materialization-handoff.md` | disc | `user-approved` | Human承認後にEpic Nodeを作成するhandoff。 |
| `20260716t131924z-01-research-initiative-bootstrap-repository-baseline.md` | research | `source-grounded` | 既存init-00322とrepository baselineの調査。 |
| `20260716t235120z-01-interview-initiative-goal-authority-and-simplification.md` | interview | `user-approved` | 回答済みInterview: 最終回答、代替、tradeoff、canonical含意。 |
| `20260716t235120z-02-interview-integrated-planning-and-document-authority.md` | interview | `user-approved` | 回答済みInterview: 最終回答、代替、tradeoff、canonical含意。 |
| `20260716t235120z-03-interview-review-protocols-scope-and-perspectives.md` | interview | `user-approved` | 回答済みInterview: 最終回答、代替、tradeoff、canonical含意。 |
| `20260716t235120z-04-interview-repair-batch-executor-and-git-boundaries.md` | interview | `user-approved` | 回答済みInterview: 最終回答、代替、tradeoff、canonical含意。 |
| `20260716t235120z-05-interview-delivery-topology-pr-and-finish-semantics.md` | interview | `user-approved` | 回答済みInterview: 最終回答、代替、tradeoff、canonical含意。 |
| `20260716t235120z-06-interview-skill-agent-oracle-and-model-policy.md` | interview | `user-approved` | 回答済みInterview: 最終回答、代替、tradeoff、canonical含意。 |
| `20260716t235120z-07-disc-planning-authority-and-yagni-rationale.md` | disc | `synthesized` | Planning authorityと簡素化原則のrationale synthesis。 |
| `20260716t235120z-08-disc-review-architecture-decision-rationale.md` | disc | `synthesized` | Review Protocol／Scope／Perspectiveのrationale synthesis。 |
| `20260716t235120z-09-disc-repair-and-delivery-decision-rationale.md` | disc | `synthesized` | Repair／Executor／Delivery lifecycleのrationale synthesis。 |
| `20260716t235120z-10-disc-skill-topology-and-global-cutover-rationale.md` | disc | `synthesized` | Skill／Agent topologyとglobal cutoverのrationale synthesis。 |
| `20260716t235120z-11-research-openai-codex-review-target-and-scope-model.md` | research | `synthesized` | OpenAI CodexのReview target／scope公開実装調査。 |
| `20260716t235120z-12-research-oracle-thin-adapter-and-github-binding.md` | research | `synthesized` | Oracle thin adapter／GitHub exact binding調査。 |
| `20260716t235120z-13-research-current-repository-workflow-gap-and-migration-impact.md` | research | `synthesized` | 現行repositoryとvNextのworkflow gap／migration impact調査。 |
| `20260716t235120z-14-disc-artifact-index-interview-discussion-research.md` | disc | `synthesized` | 回答済みInterview: 最終回答、代替、tradeoff、canonical含意。 |
| `20260716t235120z-15-disc-enriched-artifact-set-internal-self-review.md` | disc | `synthesized` | 拡張後パッケージ全体の整合性・参照・stale decision検査。 |

## Artifact Role Model

```text
canonical requirement/design/plan
        ↑ adopted decisions
accepted ADR
        ↑ durable tradeoff
Current Effective Decision Snapshot
        ↑ current decision synthesis
Interview
        ↑ human answer capture
Discussion
        ↑ cross-answer rationale
Research
        ↑ source-grounded facts
Workbench／raw session／conversation
        ↑ temporary or audit evidence
```

## Interview Normalization Policy

- 一つのInterviewは一つの本質的な質問を扱う。
- 過去の回答が後から上書きされた場合、旧回答を現行運用規則として残さず、最終回答へ正規化する。
- 代替案はtradeoff説明のために残すが、`Rejected`／`Accepted`を明記する。
- 個々の逐次会話、重複質問、音声入力の言い直しは再録しない。
- 後続Agentが実行すべき内容はcanonical三文書とADRへ反映し、Interviewだけをauthorityとして実行しない。

## Discussion Policy

- Discussionは「なぜこの決定になったか」を説明する。
- Current Effective Decision Snapshotの決定本文を複製するだけでなく、共通原則、選択肢、tradeoff、棄却理由、実装への含意を整理する。
- hidden chain-of-thought、private reasoning、raw transcriptを保存しない。
- exact field／file／Prompt等が未確定なら、未確定と明記してEpic Planningへ渡す。

## Research Policy

- `facts`、`inference`、`unverified`を混ぜない。
- 公開実装とhosted serviceを同一視しない。
- current repository commitや外部tool versionは調査固定点として明記する。
- 未検証事項はlive smoke／Epic Planningの作業として残し、事実として採用しない。

## Placement

本packを採用する際は、`artifacts/`内のfileを既存Initiativeの`artifacts/`直下へflat copyする。Interview／Discussion／Researchはcanonical三文書を上書きせず、後続Epic Planningのcontext packとして利用する。

## 更新規則

- 現在有効なDecisionが変わる場合は、Current Effective Decision Snapshotを最新状態へ再生成する。
- accepted ADRを変更する場合はsuperseding ADRを作成する。
- Interviewは新しい人間判断が必要な場合だけ追加する。
- Researchはsource versionやrepository commitが変わり、判断へ影響する場合に更新または新規作成する。
- pack内fileを変更した場合は`MANIFEST.json`と`CHECKSUMS.sha256`を再生成する。
