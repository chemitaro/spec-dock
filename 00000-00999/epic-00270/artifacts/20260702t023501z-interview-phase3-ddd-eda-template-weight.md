---
種別: interview
ID: "20260702t023501z-interview"
タイトル: "Phase 3 DDD EDA Template Weight"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t020503z-disc"
  - "20260702t014409z-research"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T02:35:01Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t020503z-disc-phase3-initiative-epic-template-model.md"
  - "artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md"
reflected_to: []
---

# 20260702t023501z-interview Phase 3 DDD EDA Template Weight

## 正式質問として扱う理由

- 影響する artifact:
  - `design.md`:
    - Initiative/Epic template の設計思想と抽象度に影響する。
  - `plan.md`:
    - Issue 01/02 の template redesign acceptance criteria に影響する。
  - `ADR`:
    - SpecDockをDDD/EDA寄りにする長期判断が必要ならADR候補になる。
- chat 上の軽微な一問では足りない理由:
  - V3はDDD/EDA由来の有用な構造を含む一方、「SpecDockをDDD-only toolにしない」と明示している。テンプレートの重さを間違えると、利用者体験と汎用性に大きく影響する。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - Initiative/Epic templates に DDD/EDA 構造をどの程度、標準セクションとして入れるか。
- 回答が後続判断へ与える影響:
  - Template section names、optional diagrams、required vs optional fields、smoke tests の期待値が変わる。

## 質問

- pressure-test question:
  - DDD/EDA構造は上流計画に役立ちますが、入れすぎるとSpecDockがDDD/EDA専用ツールに見えます。どのバランスにしますか。
- 質問:
  - Initiative/Epic templates に DDD/EDA 由来の構造をどの程度入れますか。
- 回答してほしいこと:
  - A / B / C のどれに近いかを教えてください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - V3 `initiative-design-playbook.md` は capability landscape、subdomain/investment profile、context map delta、source of truth、strategic invariants、transition architecture を提案している。
  - V3 `epic-design-playbook.md` は target model/aggregate envelope、lifecycle/state model、shared invariants、command/query/event portfolio、contract portfolio、consistency model、design slice catalog を提案している。
  - V3 guardrails は「Do not convert this into a DDD-only tool」と明示している。
  - Current Initiative templates are thin generic scaffolds.
  - Current Epic templates already include domain model, contract, data boundary, flow, state/activity, failure, migration, observability/security, test strategy sections.
- local context で解決できたこと:
  - DDD/EDAを完全排除する必要はない。V3の中心分析に含まれる。
  - ただし、すべてを必須化すると過剰。
  - Templates should be human-readable and agent-usable.
- まだ人間判断が必要な理由:
  - 汎用ツールとしての使いやすさと、ドメイン設計の表現力のバランスはproduct directionの判断を含む。

## 回答案

- Option A:
  - 軽め。DDD/EDA語彙はほぼ補足に留め、標準テンプレートは一般的なcapability/contract/workflow用語中心にする。
- Option B:
  - 中程度。標準テンプレートには汎用名のsectionを置き、DDD/EDA概念は「必要時」「例」「言い換え」として入れる。例: `Target Capability / Model Envelope` に aggregate はoptional、`Operation / Command / Query / Event Portfolio` は必要時、`Context / Source of Truth` はDDDに限定しない。
- Option C:
  - 強め。DDD/EDAを標準設計語彙として前面に出し、Initiative/Epic templates に subdomain/context/aggregate/event などを主要sectionとして入れる。

## Codex の分析

- 判断軸:
  - DDD/EDA以外のプロジェクトでも自然に使えるか。
  - Coding agent が設計境界を具体化しやすいか。
  - Templates が重くなりすぎないか。
  - V3の分析資産を活かせるか。
- tradeoff:
  - Option A は軽いが、V3が目指す upstream planning model の具体性が落ちる。
  - Option B は汎用性と設計力のバランスがよい。DDD/EDAは使えるが、使わないプロジェクトも窮屈にならない。
  - Option C は強いモデル化を促すが、SpecDockの用途を狭く見せる。
- リスク:
  - 軽すぎると、現行テンプレートの薄さがあまり改善されない。
  - 重すぎると、利用者が不要なDDD/EDA欄を埋める作業に引っ張られる。
  - smoke tests がDDD語彙の存在だけを要求すると、テンプレートの汎用性を壊す。

## Codex の推奨案

- 推奨:
  - Option B。
- 理由:
  - V3のguardrail「DDD-onlyにしない」と、V3のplaybookが持つ設計構造の両方を満たす。
  - Initiative/Epic template の標準sectionは汎用語彙にしつつ、必要時のDDD/EDA補助欄を持てる。
  - downstream Issue handoffに必要なsource-of-truth、lifecycle、contract、invariant、design sliceはDDD/EDAでなくても必要。
- 未回答時の影響:
  - Issue 01/02 の template redesign scope と acceptance criteria が固定できない。

## ユーザー回答

- answer capture:
  - Option A を採用する。ただし、DDD/EDA を完全に扱えないようにするのではなく、標準テンプレートをDDD/EDA語彙に縛らない。
  - SpecDock 自体はDDDでもイベントドリブンアーキテクチャでもない軽量CLIツールであり、DDD/EDAに寄せすぎるとノイズになる。
  - 既存コードや既存設計方針からアーキテクチャが明確な場合は、それに従う。
  - アーキテクチャや設計方針が未定の場合は、ユーザーインタビュー等を通じて、Initiative層で設計方針やアーキテクチャを具体化してから要件・設計・計画へ落とす。
  - DDD/EDAが適切なプロジェクトでは、DDD/EDAに沿った整理や設計も行えるようにする。
- 回答:
  - Initiative/Epic templates は DDD/EDA語彙を標準前提にしない軽量・汎用寄りにする。既存アーキテクチャが明確ならそのアーキテクチャに合わせ、未定なら上位層で設計方針を明確化する。DDD/EDAは必要な場合に使える補助モデルとして扱う。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Artifact adoption を templates/reviewer でどこまで必須化するか。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `design.md` / `plan.md` / Issue 01-02 acceptance criteria / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - SpecDock自身の性質と汎用性を踏まえ、DDD/EDAを標準前提にしない一方で、既存または選択されたアーキテクチャに合わせられる方針が明示されたため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - 汎用性 / non-goal として、SpecDockをDDD/EDA専用ツールにしないことを反映する。
- `design.md`:
  - Template design principles として、architecture-aware but architecture-neutral を反映する。
- `plan.md`:
  - Initiative/Epic template redesign Issues の acceptance criteria に、既存アーキテクチャ適合・未定時の上位層clarification・DDD/EDA optional support を反映する。
- `ADR`:
  - 長期product directionとしてADR候補になり得るが、現時点ではcanonical docs/reportへの採用で足りる見込み。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - Canonical docs / report ledger への反映は次工程。
