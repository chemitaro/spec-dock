---
kind: disc
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T04:13:43Z
created_by: codex
status: answered
authority: synthesized
derived_from:
  - mattpocock-skills-source/skills/productivity/grill-me/SKILL.md
  - mattpocock-skills-source/skills/engineering/grill-with-docs/SKILL.md
  - requirement.md
reflected_to: []
---

# grill essence integration review

## 位置づけ

この文書は、Matt Pocock 氏の `grill-me` / `grill-with-docs` の essence が、今回の spec-dock 要件にうまく統合されているかを、第三者の客観的な consultant 視点で分析した記録である。

分析の目的は、追加された workflow、template、agent boundary、recording rule によって、元 skill の強みが薄まっていないかを確認することである。

## 結論

現時点の `requirement.md` は、元 skill の essence をかなり高い精度で spec-dock-native に翻訳できている。

特に、次の変換は妥当である。

- `CONTEXT.md` を新しい正本にせず、spec-dock の active docs、parent docs、`discussions/`、source、tests、templates を context source とする。
- discussion artifact を canonical source of truth にせず、採用判断を経て `requirement.md` / `design.md` / `plan.md` / ADR へ昇格させる。
- 一問一答、Codex の推奨案提示、回答を待って次に進む流れを標準の人間問い合わせ方法にする。
- repo / docs / code で解けることを人間に聞かない。
- 専門 agent の質問事項を orchestrator が取りまとめ、人間には orchestrator が一問ずつ問い合わせる。
- grill 専用 template を増やさず、既存の `interview` / `research` / `disc` / `adr` / `report` を共通 template として再設計する。

一方で、元 skill のうち、用語を鋭利化する力、具体シナリオで境界を詰める力、ADR を濫発しない判断条件は、現 requirement ではやや弱くなっている。

## essence mapping

| 元 skill の essence | 現 requirement の反映 | 評価 |
|---|---|---|
| 共有理解に到達するまで plan / design を徹底的に詰める | clarification workflow、canonical docs への反映として保持されている | 強い |
| decision tree を一枝ずつ進み、依存する判断を順に解消する | 一問一答、質問シート、中間レポート、上位レポートの流れとして保持されている | 強い |
| 質問は一つずつ行い、回答を待って進める | 標準質問スタイル、受け入れ条件、非交渉制約として明確 | 強い |
| 各質問に Codex の推奨回答を添える | 質問シートと質問運用の必須要素として明確 | 強い |
| repo / docs / code で解けることは人間に聞かない | source-grounding として明確 | 強い |
| domain language を既存 docs / source と照合し、曖昧語を鋭利化する | source-grounding に含まれるが、用語衝突や overloaded terms の扱いは明示が薄い | 中 |
| 決定を docs / ADR に反映し、ADR は sparingly に扱う | canonical reflection は強いが、ADR candidate の絞り込み条件は弱い | 中 |

## よく統合できている点

元 skill は、単に質問を増やすための workflow ではなく、曖昧な理解のまま実装へ進まないための shared understanding workflow である。

現 requirement は、この点を spec-dock の構造に合わせてよく翻訳している。

- `grill-me` の一問一答性は、agent-to-human question style として取り込まれている。
- `grill-me` の recommended answer は、質問シートと会話上の質問における Codex recommendation として取り込まれている。
- `grill-with-docs` の docs-aware challenge は、active docs、parent docs、discussion history、source/tests/templates を確認してから質問する source-grounding として取り込まれている。
- `grill-with-docs` の documentation update は、discussion artifact から canonical docs / ADR への promotion lifecycle として取り込まれている。
- spec-dock の authority model に合わせ、discussion は根拠と議論の記録、canonical docs は採用済み正本として分離されている。

このため、元 skill の essence は「直接移植」ではなく「spec-dock の作法への再定式化」として統合されている。

## 薄まりかけている点

### 1. 用語を鋭利化する力

`grill-with-docs` の強みは、単に docs を読むことではなく、既存の domain model、用語、責務境界と突き合わせて、曖昧な言葉を実装可能な語彙へ sharpening する点にある。

現 requirement は source-grounding を強く定義しているが、次の観点はやや弱い。

- 既存 docs / source と user wording の用語衝突を検出する。
- 同じ語が複数の意味で使われている場合に問い直す。
- 具体シナリオや edge case を使って責務境界を確認する。
- canonical term に寄せるか、新しい用語を導入するかを明示する。

### 2. 具体シナリオで境界を詰める力

元 skill の grill は抽象的な質問だけではなく、現実のケース、例外、境界条件を使って理解を深める。

現 requirement では decision tree や質問シートは整っているが、質問が形式的な option selection に寄ると、具体例による検証が弱くなる可能性がある。

### 3. ADR を濫発しない条件

現 requirement は ADR candidate や promotion lifecycle を持つが、元 skill の「ADR は sparingly」という判断基準がやや薄い。

ADR candidate は、少なくとも次のような条件を満たす場合に限るべきである。

- 後から戻すのが難しい。
- 将来の読者にとって意外性がある。
- 実質的な tradeoff がある。

### 4. PlantUML の制度化リスク

PlantUML は理解を助ける場合に有用だが、全質問シートで必須化すると過剰制度化になる。

現 requirement には、PlantUML が必須のように読める箇所と、条件付きの補助要素として読める箇所が混在している可能性がある。

## 過剰制度化リスク

形式化そのものは spec-dock との統合に必要である。

ただし、正式質問シート、中間レポート、reflection ledger の運用が強くなりすぎると、元 skill の軽快な壁打ちと relentless な追求が、「証跡を作るための質問」にすり替わるリスクがある。

現在の方針では、軽微な確認は chat 上の一問でよく、重要判断のみ正式質問シートを作成するため、このリスクは許容範囲に収まっている。

このバランスは維持すべきである。

## 要件への補正候補

現 requirement の方向性は妥当であり、大きなやり直しは不要である。

補正するなら、最小限で次の 3 点を追加するのがよい。

1. PlantUML は必須ではなく、理解に資する場合の条件付き要素であると明確化する。
2. 用語、責務境界、domain relationship が曖昧または既存 docs / source と衝突する場合は、具体シナリオや edge case を使って境界を明確化する。
3. ADR candidate は、hard to reverse、surprising without context、real tradeoff の少なくともいずれかを満たす場合に限って検討する。

## 人間への追加質問

なし。

この分析から見る限り、要件の方向性は既に十分に固まっている。

必要なのは追加ヒアリングではなく、上記の補正候補を `requirement.md` に小さく反映するかどうかの判断である。
