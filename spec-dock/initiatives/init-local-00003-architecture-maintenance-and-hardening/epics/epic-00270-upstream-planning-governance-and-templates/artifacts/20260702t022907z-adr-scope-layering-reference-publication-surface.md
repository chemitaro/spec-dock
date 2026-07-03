---
種別: ADR（Architecture Decision Record）
ID: "20260702t022907z-adr"
タイトル: "Scope Layering Reference Publication Surface"
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
  - "artifacts/20260702t021107z-interview-phase3-scope-layering-publication-surface.md"
  - "artifacts/20260702t022727z-research-deep-consultant-scope-layering-publication-recommendation.md"
  - "artifacts/20260702t020503z-01-disc-phase3-scope-authority-model.md"
reflected_to:
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260702t022907z-adr Scope Layering Reference Publication Surface

## ADR 化基準

- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `design.md` / `plan.md` / `report.md`
- ADR として残す理由:
  - scope-layering / Initiative-Epic-Issue責務モデルは、今回のEpic内だけでなく、将来のSpecDock authoring agents が継続的に参照する横断ルールになる。
  - 新規provider docsを1つ追加する判断は、ファイル増殖と情報分散のtradeoffを含むため、文脈なしでは意図が伝わりにくい。
  - 後続Issueで docs / skills / templates / smoke tests を更新するときの境界判断として再利用される。

## 結論（Decision）

`scope-layering / Initiative-Epic-Issue責務モデル` は、1つの provider-side canonical reusable reference として公開する。

作成する公開面:

```text
src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md
```

この reference は、次を扱う狭いhubとする。

- Initiative / Epic / Issue / Issue Plan / Report の scope ownership table
- decision-radius rule
- artifact -> canonical docs / ADR -> report Evidence Adoption Ledger の authority flow
- anti-rules:
  - decision-only Issue を execution-ready として作らない
  - raw artifact を canonical authority として扱わない
  - Issue plan が親 requirement/design decision を作らない

既存の workflow docs / phase docs / skills / templates は、責務表を重複して持たず、必要箇所から `authoring/scope-layering.md` へ薄くリンクする。

ADR は日常の参照面にはしない。このADRは、なぜ1つのprovider referenceを追加するのかという設計判断を記録する。

## 背景（Context）

V3 planning pack は、scope-layering / Initiative-Epic-Issue responsibility model / discovery artifact adoption / Epic-to-Issue slicing を Epic-level design/plan の前提として提示している。

一方で、これらをどの公開面で維持するかにはtradeoffがある。

- 新規ファイルを増やしすぎると、後続エージェントが適切な情報へ到達しにくくなる。
- 既存workflow docsやtemplatesへ分散させすぎると、責務モデルが散らばり、表現driftや参照漏れが起きる。
- ADRだけに置くと、日常的に authoring / planning するエージェントのfirst-read surfaceとして弱い。

fresh deep-consultant analysis は、1つの狭いprovider referenceをhubにし、既存docs/skills/templatesは薄くリンクするhybridを推奨した。

## 選択肢（Options considered）

- 選択肢 A:
  - 概要:
    - `docs/authoring/scope-layering.md` を追加し、scope ownership / decision-radius / authority flow の唯一の再利用referenceにする。
  - 良い点（Pros）:
    - 後続エージェントが最初に見る場所が明確になる。
    - workflow docs / templates / skills で同じ表を重複させずに済む。
    - V3 referenceを活かしつつ、canonical docsへ全文貼りしない方針と整合する。
  - 悪い点 / 制約（Cons）:
    - provider docs が1ファイル増える。
    - workflow docsとの矛盾を防ぐリンク/grep/smoke checks が必要。
  - 採用理由:
    - 最小の新規ファイル数で、情報分散とファイル増殖の両方を抑えられる。
- 選択肢 B:
  - 概要:
    - 新規referenceは作らず、workflow / phase / template / skill に必要箇所だけ分散して埋め込む。
  - 良い点（Pros）:
    - 新規ファイルは増えない。
  - 悪い点 / 制約（Cons）:
    - 同じscope tableや責務表現が複数箇所に散り、driftしやすい。
    - 後続エージェントが全体像に到達しにくい。
  - 棄却理由:
    - 今回のモデルは横断lookup ruleであり、分散配置に向かない。
- 選択肢 C:
  - 概要:
    - ADRを主たる公開面にし、docs/templates/skills はADR参照にする。
  - 良い点（Pros）:
    - 判断の長期性は明確に残る。
  - 悪い点 / 制約（Cons）:
    - 日常のauthoring agent が最初に見るsurfaceとして弱い。
    - ADRを読まないとテンプレートやworkflowの使い方が分からなくなる。
  - 棄却理由:
    - ADRは採用理由の記録に留め、運用上のfirst-read surfaceはprovider docsに置く方がよい。

## 判断理由（Rationale）

この判断は「ファイルを作ればよい」でも「ファイルを作らなければよい」でもない。

scope-layering model は、Initiative / Epic / Issue / Issue Plan / Report をまたぐ横断的なrouting ruleであり、workflow lifecycleやphase authoringの一部ではあるが、それらのどれか単独に閉じない。

そのため、1つだけ狭いreferenceを作り、既存surfaceはそこへリンクするのが最適なinformation architectureである。

この形なら:

- provider docsに再利用可能な正本がある。
- workflow docs は lifecycle authority のまま保てる。
- `decision-routing.md` は例やrouting patternsのguideのまま保てる。
- templates はtutorial化せず薄いscaffoldのまま保てる。
- ADRは意思決定の理由を記録し、日常の参照面にはしない。

## 影響（Consequences）

- 良い影響（Positive）:
  - 後続エージェントが scope ownership を探す入口が明確になる。
  - V3 reference を無視せず、かつ全文貼り/重複を避けられる。
  - docs/skills/templates 間の責務表現driftを抑えられる。
- 悪い影響 / 将来負債（Negative / Debt）:
  - `scope-layering.md` が大きくなりすぎると第二のworkflow manualになる。
  - 既存workflow docsからのリンク漏れがあると、新referenceが発見されにくい。
- 影響範囲（コード/テスト/運用/データ）:
  - provider docs:
    - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
    - `authoring/decision-routing.md`
    - `workflow_initiative.md`
    - `workflow_epic.md`
    - `workflow_issue.md`
    - phase plan docs
  - provider skills:
    - initiative / epic / issue planning skills
    - epic execution skill where parent-scope decision gaps are routed
  - tests:
    - provider doc presence
    - required inbound links
    - no duplicated full responsibility table
    - no local artifact path as provider authority
    - template thinness
- 移行/ロールバック:
  - If `scope-layering.md` becomes too broad, move lifecycle details back to workflow docs and keep only responsibility/routing rules in the reference.
  - If future reviewer evidence shows this should not be provider-wide, downgrade links and keep the model in Epic design/plan only.
- 追加対応（Follow-ups / Epic / Issue / ADR）:
  - Epic plan should assign the docs/skills update to the planning docs/skills Issue.
  - Epic plan should assign smoke checks to the smoke/template validation Issue.
  - No additional ADR is needed unless validation semantics or global architecture commitments change.

## 参考（References）

- 関連仕様（requirement/design/plan/report）:
  - `epic-00270/design.md` (planned reflection)
  - `epic-00270/plan.md` (planned reflection)
  - `epic-00270/report.md` Evidence Adoption Ledger
- 元になった artifacts（derived_from）:
  - `artifacts/20260702t021107z-interview-phase3-scope-layering-publication-surface.md`
  - `artifacts/20260702t022727z-research-deep-consultant-scope-layering-publication-recommendation.md`
  - `artifacts/20260702t020503z-01-disc-phase3-scope-authority-model.md`
  - `artifacts/20260702t020436z-01-disc-phase3-reference-adoption-map.md`
- 反映先（reflected_to）:
  - `design.md`
  - `plan.md`
  - `report.md`
