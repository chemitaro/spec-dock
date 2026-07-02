---
種別: ADR（Architecture Decision Record）
ID: "20260702t040113z-adr"
タイトル: "Japanese First Spec Authoring Policy"
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
  - "user clarification on 2026-07-02"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260702t040113z-adr Japanese First Spec Authoring Policy

## ADR 化基準

- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md` / `design.md` / `plan.md` / `report.md`
- ADR として残す理由:
  - SpecDock の主要利用者は日本語で要件・設計・計画を作成している。
  - これまでの仕様作成では、要件定義書、設計書、実装計画書、artifacts に英語が混ざりやすかった。
  - 日本語での仕様書作成をテンプレート、skills、workflow、reviewer gate、tests に組み込まないと、今後も同じ品質問題が再発する。

## 結論（Decision）

SpecDock の日本語運用では、要件定義書、設計書、計画書、report、artifacts を日本語ファーストで作成する。

ファイル名、ID、コマンド名、コード識別子、SpecDock の固定用語、外部固有名詞は原文のまま保持してよい。ただし、説明文、判断理由、受け入れ条件、設計説明、計画説明、reviewer向けの指示、artifact本文は日本語で書く。

テンプレート、planning skills、workflow docs は、この方針を明示する。特に次を対象とする。

- Initiative / Epic / Issue の requirement / design / plan templates
- artifacts の作成 guidance
- report の Evidence Adoption Ledger / Spec Authoring Gate guidance
- planning / clarification / execution skills
- reviewer gate と smoke tests

英語を完全に禁止するのではなく、次の用途に限定して許容する。

- ファイルパス、コマンド、設定値、API名、class / function / variable 名
- `Issue`、`Epic`、`ADR`、`artifact`、`spec-reviewer` など、SpecDock の既存固定語
- 引用、外部資料名、ライブラリ名、GitHub / CI / CLI の実名
- 日本語に訳すと意味が曖昧になる短い専門語

許容される英語であっても、文全体が英語の説明になる場合は日本語へ書き直す。

## 背景（Context）

今回の Epic planning でも、途中から設計書と計画書の説明が英語へ寄っていた。これは単発の表記揺れではなく、SpecDock のテンプレートや skills が日本語 authoring を十分に誘導できていないことの症状である。

SpecDock は日本語での協働開発・dogfooding に使われている。要件・設計・計画・artifact が英語混在になると、読み返し、レビュー、意思決定の復元、次のAIエージェントへの handoff の負荷が上がる。

一方で、技術用語やコード識別子まで無理に翻訳すると、検索性や正確性が落ちる。そのため、日本語ファーストと技術識別子の保持を両立する方針が必要である。

## 選択肢（Options considered）

- 選択肢 A:
  - 概要:
    - 仕様文書と artifacts の本文を日本語ファーストにし、技術識別子や固定語だけ英語を許容する。
  - 良い点:
    - 日本語での読み返しとレビューが安定する。
    - コード検索やコマンドの正確性を損なわない。
    - 既存の SpecDock 用語との互換性を維持できる。
  - 悪い点 / 制約:
    - reviewer / smoke test で自然言語品質を完全には機械判定できない。
  - 採用理由:
    - 日本語運用に最も合い、かつ技術情報の正確性も保てるため。
- 選択肢 B:
  - 概要:
    - 英語混在を許容し、必要時だけ人間が直す。
  - 良い点:
    - 実装コストは低い。
  - 悪い点 / 制約:
    - 同じ問題が繰り返される。
    - 後工程のレビュー負荷が高い。
  - 棄却理由:
    - 今回のユーザー補足により、再発防止が Epic scope として必要になったため。
- 選択肢 C:
  - 概要:
    - 英語を全面禁止する。
  - 良い点:
    - 表記方針は単純になる。
  - 悪い点 / 制約:
    - ファイルパス、コマンド、コード識別子、外部固有名詞まで不自然に翻訳される危険がある。
  - 棄却理由:
    - 技術的正確性と検索性を損なうため。

## 判断理由（Rationale）

仕様書の目的は、将来の自分とAIエージェントが要件、設計判断、実装計画、残課題を復元できるようにすることである。日本語で進めているプロジェクトでは、仕様本文が日本語で揃っていること自体が品質要件になる。

ただし、技術識別子の翻訳は誤解を生む。したがって、本文の説明・判断・受け入れ条件は日本語にし、識別子・固定語・外部固有名詞は原文を保持する。

この方針は、単に今回の `requirement.md` / `design.md` / `plan.md` を直すだけでなく、今後のテンプレート、skills、workflow docs、reviewer guidance、validation に反映する。

## 影響（Consequences）

- 良い影響:
  - 要件定義書、設計書、計画書、artifacts の読み返しやすさが上がる。
  - 日本語での interview / ADR / canonical authoring の流れが安定する。
  - 次のAIエージェントが、英語混在による文脈のズレを起こしにくくなる。
- 悪い影響 / 将来負債:
  - 日本語品質の完全な機械判定は難しい。
  - 許容英語と過剰な英語混在の境界を reviewer が判断する必要がある。
- 影響範囲:
  - Initiative / Epic / Issue templates
  - artifacts guidance
  - planning / clarification / execution skills
  - workflow / phase docs
  - report ledger guidance
  - smoke tests / reviewer checks
- 移行 / rollback:
  - 既存 historical artifacts は grandfathered evidence として残し、無理に全文翻訳しない。
  - 新規作成・更新される canonical docs と artifacts から日本語ファーストを適用する。
  - もし日本語化により技術的精度が落ちる場合は、該当する識別子や外部固有名詞だけ原文を残す。

## 参考（References）

- 関連仕様:
  - `epic-00270/requirement.md`
  - `epic-00270/design.md`
  - `epic-00270/plan.md`
  - `epic-00270/report.md`
- 元になった入力:
  - 2026-07-02 のユーザー補足: 「日本語の要件定義書、設計書、実装計画書、あとアーティファクトも日本語、これを実施できるようにしてください」
- 反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
