---
種別: ADR（Architecture Decision Record）
ID: "20260702t024118z-adr"
タイトル: "Architecture Neutral Template Authoring Policy"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-07-02"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from:
  - "artifacts/20260702t023501z-interview-phase3-ddd-eda-template-weight.md"
  - "artifacts/20260702t020503z-disc-phase3-initiative-epic-template-model.md"
  - "artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260702t024118z-adr Architecture Neutral Template Authoring Policy

## ADR 化基準

- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md` / `design.md` / `plan.md`
- ADR として残す理由:
  - Initiative/Epic templates の抽象度と語彙選択は、今後の SpecDock authoring experience 全体に影響する。
  - DDD/EDA の設計語彙は有用だが、標準前提にすると軽量CLIや非DDD/非EDAプロジェクトでノイズになる。
  - 一方で、DDD/EDA が適切なプロジェクトでは、それに沿った要件整理・設計・計画もできる必要がある。

## 結論（Decision）

SpecDock の Initiative/Epic templates は、DDD / EDA を標準前提にしない。

標準テンプレートは architecture-neutral / architecture-aware とする。

- architecture-neutral:
  - DDD / EDA / Clean Architecture など特定の設計流派を標準前提にしない。
  - 軽量CLI、docs tooling、single-process utility などにも自然に使える語彙を優先する。
- architecture-aware:
  - 既存コードや既存docsからアーキテクチャや設計方針が明確な場合は、それに従う。
  - アーキテクチャや設計方針が未定の場合は、Initiative 層でユーザーインタビューや調査により設計方針を具体化してから Epic / Issue へ下ろす。
  - DDD / EDA が適切なプロジェクトでは、必要時の補助モデルとして DDD / EDA の語彙や設計欄を使えるようにする。

このため、templates では次のような汎用表現を優先する。

- `Capability / Model Envelope`
- `Context / Source of Truth`
- `Lifecycle / State`
- `Operation / Command / Query / Event Portfolio`
- `Contract Portfolio`
- `Invariant / Constraint`
- `Design Slice / Handoff`

`Aggregate`, `Bounded Context`, `Domain Event`, `Subdomain`, `EventStorming` などの DDD / EDA 語彙は、必要時の例・言い換え・任意補助欄として扱う。

## 背景（Context）

V3 planning pack には DDD / EDA 由来の分析語彙が多く含まれている。これらは upstream planning を具体化するうえで有用である。

しかし、SpecDock 自体は DDD でも EDA でもない。軽量CLIツール、scaffold tool、docs workflow tool としての性格が強く、DDD / EDA に寄せすぎると、自身のdogfoodingでも不要なノイズが発生する。

また、SpecDock は特定アーキテクチャへ誘導するためのツールではなく、既存プロジェクトの source-of-truth / workflow / planning を扱うツールである。したがって、既存アーキテクチャが明確な場合はそれに従い、未定の場合だけ上位層で明確化する方が自然である。

## 選択肢（Options considered）

- 選択肢 A:
  - 概要:
    - DDD / EDA 語彙は標準前提にせず、汎用的な capability / context / contract / workflow / model envelope 用語を中心にする。
  - 良い点（Pros）:
    - 軽量CLIや非DDD/非EDAプロジェクトでも使いやすい。
    - SpecDock自身のdogfoodingに合う。
    - テンプレートが過剰に重くならない。
  - 悪い点 / 制約（Cons）:
    - DDD / EDA を使いたいプロジェクトには補助欄や例が必要。
  - 採用理由:
    - 汎用ツールとしての自然さを保ちつつ、必要時に DDD / EDA を利用できるため。
- 選択肢 B:
  - 概要:
    - 汎用section名を標準にしつつ、DDD / EDA 概念を必要時の例・言い換えとして入れる。
  - 良い点（Pros）:
    - DDD / EDA サポートと汎用性のバランスが取れる。
  - 悪い点 / 制約（Cons）:
    - 実装時に例が増えすぎるとテンプレートが重くなる。
  - 採用方法:
    - Option A の補助挙動として採用する。標準前提ではなく、必要時の支援として扱う。
- 選択肢 C:
  - 概要:
    - DDD / EDA を標準設計語彙として前面に出す。
  - 良い点（Pros）:
    - ドメイン設計やイベント駆動設計のプロジェクトでは強力。
  - 悪い点 / 制約（Cons）:
    - SpecDock を DDD / EDA 専用ツールに見せる。
    - 軽量CLIなどではノイズになる。
  - 棄却理由:
    - V3 guardrail の `Do not convert this into a DDD-only tool` と矛盾する。

## 判断理由（Rationale）

テンプレートは、ユーザーに特定のアーキテクチャを強制するものではなく、対象プロジェクトの設計方針を正しく発見・反映するための道具である。

そのため、テンプレートは次の順序で振る舞うべきである。

1. 既存コード・docs・tests・runtime構造から設計方針を読み取る。
2. 設計方針が明確なら、その方針に従って Initiative / Epic / Issue を具体化する。
3. 設計方針が未定または矛盾している場合は、Initiative 層で調査・ユーザーインタビュー・ADR候補により方針を明確化する。
4. DDD / EDA は、対象プロジェクトに適合する場合だけ補助モデルとして使う。

この方針により、SpecDock は軽量なCLIツールにも、DDD / EDA が必要な大きなドメインシステムにも対応できる。

## 影響（Consequences）

- 良い影響（Positive）:
  - Templates が特定アーキテクチャに縛られず、幅広いプロジェクトに使える。
  - 既存コードとdocsから設計方針を読む姿勢が強化される。
  - DDD / EDA が必要な場合には、補助モデルとして自然に利用できる。
- 悪い影響 / 将来負債（Negative / Debt）:
  - DDD / EDA 専用テンプレートほど強い誘導はできない。
  - 汎用section名にした場合、説明文や例で適切な設計深度を補う必要がある。
- 影響範囲（コード/テスト/運用/データ）:
  - Initiative requirement/design/plan templates
  - Epic requirement/design/plan templates
  - planning skills
  - workflow / phase docs
  - template smoke tests
- 移行/ロールバック:
  - If templates become too generic and lose design power, add optional guidance/examples rather than making DDD/EDA mandatory.
  - If templates become too DDD/EDA-heavy, move specialized terms into optional examples or reference docs.
- 追加対応（Follow-ups / Epic / Issue / ADR）:
  - Issue 01 and Issue 02 should encode architecture-neutral section names.
  - Smoke tests should not require DDD/EDA-specific terms as mandatory sections.
  - Reviewer guidance should check whether the chosen architecture matches repository evidence.

## 参考（References）

- 関連仕様（requirement/design/plan/report）:
  - `epic-00270/design.md` (planned reflection)
  - `epic-00270/plan.md` (planned reflection)
  - `epic-00270/report.md` Evidence Adoption Ledger
- 元になった artifacts（derived_from）:
  - `artifacts/20260702t023501z-interview-phase3-ddd-eda-template-weight.md`
  - `artifacts/20260702t020503z-disc-phase3-initiative-epic-template-model.md`
  - `artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md`
- 反映先（reflected_to）:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
