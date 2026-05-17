---
種別: disc
ID: "20260517t104958z-disc"
タイトル: "question promotion record type"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-05-17"
親: ["iss-00100"]
関連: ["#100", "20260517t103746z-disc"]
---

# 20260517t104958z-disc question promotion record type

## 質問
- promotion record を独立した discussion doc type として作るべきか。

## ユーザー回答
- 独立した promotion record type は作らない。
- 文書そのものが別種別へ昇格する仕組みも作らない。
- `disc` を `adr` に昇格させるのではなく、`disc` / `research` / `interview` / `scratch` の積み上げを踏まえて、新しい `adr` を作成する。
- 作成した `adr` の内容は、必要に応じて `requirement.md` / `design.md` / `plan.md` へ織り込んで修正する。

## なぜこの判断がよいか
- 文書を昇格させる仕組みにすると、元文書の目的と新文書の責務が混ざりやすい。
- `disc` は議論の作業場であり、`adr` は決定の正本である。両者は同じファイルを状態変更するより、文脈を踏まえて別 artifact として作る方が読みやすい。
- `research` や `interview` は根拠や入力であり、そのまま決定文書に変換すると、事実・解釈・判断が混ざるリスクがある。
- 新規作成にすると、ADR 側で「何を採用したか」「何を採用しなかったか」「なぜそう決めたか」を改めて整理できる。

## 採用方針
- `promotion` / `promotion-record` は初期 doc type にしない。
- `promoted_from` / `promoted_to` のような「文書昇格」を示す field も初期設計では使わない。
- 代わりに、次のような軽い参照 field / section を使う。
  - `derived_from`: 作成時に参照した discussion docs
  - `reflected_to`: 内容を織り込んだ正本 artifact
  - `反映メモ`: どの内容をどこへ反映したか
- 反映先の正本 artifact 側には、必要に応じて関連 discussion docs を `関連` / `references` として残す。

## 具体例

```text
scratch: 作業中の断片
  ↓ 文脈を整理して新規作成
research: 技術調査
  ↓ 根拠として参照
disc: 選択肢比較
  ↓ 決定が必要になったら新規作成
adr: 意思決定記録
  ↓ 決定内容を織り込む
requirement.md / design.md / plan.md
```

## 回答後の反映先
- `requirement.md`
- `20260517t103746z-disc-discussion-template-catalog-design-proposal.md`
- 設計フェーズの common metadata / template guidance
