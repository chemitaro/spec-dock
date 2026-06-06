---
種別: draft-requirement
ID: "20260606t024154z-draft-requirement"
タイトル: "Align Templates Scaffolds Examples Draft Requirement"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["iss-00166", "epic-00158", "init-local-00003"]
authority: "proposed"
source_paths:
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md
  - spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md
intended_targets:
  - spec-dock/active/epic/issues/iss-00166-align-templates-as-scaffolds-and-examples/requirement.md
adoption_status: unreviewed
reflected_to: []
---

# iss-00166 Align Templates As Scaffolds And Examples — 要件定義ドラフト

## 目的

Templates を artifact 作成の scaffold、evidence slot、good example として整え、completion / compliance / phase promotion の authority と誤読されないようにする。

この issue は first-wave cleanup の最後に、skill/docs boundary と clarification workflow を反映したテンプレート面を揃える。

## 背景・現状

- 現状の挙動:
  - Templates は canonical docs や discussion docs の starting scaffold を提供する。
  - Report template は EAL / Spec Authoring Gate / Delegated Draft Evidence など重要な slots を持つ。
  - Discussion templates は `interview` / `research` / `disc` などを提供する。
- 現状の課題:
  - Templates が compliance authority のように読まれると、skill/docs の責務境界が崩れる。
  - Clarification grill loop を支える `interview` / `research` / `disc` の slots が不足または弱いと、質問と採用証跡が分断される。
  - Template examples が古い docs-owned workflow を示すと、first-read skill spine と矛盾する。
- 観測点:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/report.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock artifacts を作成する agent / maintainer。
- 代表シナリオ:
  - Agent が template から artifact を作成し、必要な slots と examples を得るが、template だけで phase completion や compliance pass を主張しない。

## スコープ

- 必須:
  - Templates を scaffold / evidence slot / good example として明確化する。
  - Report templates の EAL / Spec Authoring Gate / Delegated Draft Evidence slots が current workflow に合うことを確認する。
  - `interview` template は unanswered before asking / answer capture / reflection を支える。
  - `research` template は facts / uncertainty / question candidates を支える。
  - `disc` template は synthesis / ADR triage / reflection plan を支える。
  - Templates から compliance authority / reviewer pass claim / phase promotion claim と誤読される wording を避ける。
- 禁止:
  - Templates を pass/fail rule の authority にしない。
  - Skill-owned workflow を template に全文コピーしない。
  - Docs が所有すべき field semantics / hard cases を template に過剰移動しない。
  - Runtime validation を追加しない。
- 対象外:
  - Skill rewrite。
  - Workflow docs rewrite。
  - Automated regression harness。

## 境界

- 常に行う:
  - Template は「書き始めるための形」と「残すべき証跡 slot」を示す。
  - Authority は workflow docs / accepted ADR / canonical docs / reviewer gates / report ledger に置く。
  - Provider-side templates を正本として変更し、dogfooding mirror で確認する。
- 判断が必要:
  - Template に入れる example の量。
  - Report template に残す required ledger fields の粒度。
- 行わない:
  - Template placeholder をそのまま completion とみなさない。
  - Template を使っただけで spec-reviewer pass とみなさない。

## 非交渉制約

- Templates are not compliance authorities。
- Delegated draft / external evidence の adoption は `report.md` に残す。
- `interview` は重要判断で一問一答の evidence artifact として使える scaffold を持つ。

## 前提

- Skill/docs boundary、clarification workflow、workflow docs boundary が先行 issue の adopted / completed evidence として確認できる。
- Draft-only upstream evidence は analysis / inventory の参考に限り、template provider change の実装根拠にはしない。
- This is T4 templates lane and should not reopen earlier workflow policy decisions.

## 受け入れ条件

- AC-001:
  - アクター: agent
  - 前提: canonical / discussion artifact を template から作る
  - 操作: template slots を埋める
  - 期待結果: scaffold / evidence slot / example は得られるが、template 自体を compliance authority と誤認しない
  - 観測点: template wording review
- AC-002:
  - アクター: clarification を行う agent
  - 前提: important decision が必要
  - 操作: `interview` template を使う
  - 期待結果: source grounding、one question、answer capture、reflection/adoption needs を残せる
  - 観測点: template / smoke
- AC-003:
  - アクター: reviewer
  - 前提: `research` / `disc` template を確認する
  - 操作: clarification workflow の補助 artifact として見る
  - 期待結果: research と disc が human answer の代替や raw dump にならず、facts/candidates と synthesis/ADR triage を支える
  - 観測点: template diff
- AC-004:
  - アクター: maintainer
  - 前提: report template を確認する
  - 操作: EAL / delegated evidence / gate slots を見る
  - 期待結果: adoption / reviewer / blocking / next action が記録できる
  - 観測点: template diff
- AC-005:
  - アクター: maintainer
  - 前提: provider templates を変更する
  - 操作: dogfooding mirror を確認する
  - 期待結果: provider source と mirror の validation が report に残る
  - 観測点: `validate`, `sync`, targeted inspection

## 例外・エッジケース

- EC-001:
  - 条件: Template に詳細説明を入れすぎて docs と重複する
  - 期待: 詳細 semantics は docs に戻し、template は slot/example に留める
  - 観測点: review
- EC-002:
  - 条件: Template から required field が見えず evidence が欠ける
  - 期待: Slot を追加するが、authority claim は追加しない
  - 観測点: report / template inspection

## 用語（ドメイン語彙）

- TERM-001:
  - Scaffold: artifact を書き始めるための構造。
- TERM-002:
  - Evidence slot: 後続 reviewer / maintainer が採用判断を追えるようにする記録欄。
- TERM-003:
  - Good example: agent が正しい書き方を模倣しやすくする最小例。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking default:
  - Templates は short scaffold を維持し、必要な examples は多すぎない範囲で追加する。
