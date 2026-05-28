---
kind: disc
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T04:18:31Z
created_by: codex
status: answered
authority: synthesized
derived_from:
  - 20260528t041343z-disc-consultant-grill-essence-integration-review.md
  - requirement.md
reflected_to:
  - requirement.md
---

# consultant requirement update proposal

## 位置づけ

この文書は、Matt Pocock `grill-me` / `grill-with-docs` の essence integration review を踏まえて、`requirement.md` をどのように最小更新するべきかを consultant 視点で整理した記録である。

## 結論

要件の方向性を大きく変える必要はない。

現 `requirement.md` は、元 skill の essence を spec-dock-native に翻訳する骨格をすでに持っている。

したがって、補正は次の 4 点に絞る。

1. 今回の essence review と requirement update proposal を `derived_from` に追加し、補正根拠を追跡可能にする。
2. PlantUML を必須要素ではなく、理解を助ける場合の条件付き要素として統一する。
3. 用語 sharpening と、具体シナリオ / edge case による境界確認を、source-grounded clarification の一部として明示する。
4. ADR candidate は、原則として `hard to reverse`、`surprising without context`、`real tradeoff` を満たす判断に絞る。

## 反映対象

### frontmatter

`derived_from` に、今回の consultant review とこの更新提案を追加する。

### スコープ / 必須

質問シートの必須要素と条件付き要素を整理する。

目的、質問内容、回答候補、Codex の分析、Codex の推奨案は必須とする。

PlantUML 図、詳細 tradeoff、後続反映案は、質問の性質に応じて理解を助ける場合に含める。

### 境界 / 常に行う

`grill-with-docs` の essence である terminology sharpening を明示する。

用語、責務境界、domain relationship が曖昧または既存 docs / source と衝突する場合は、既存表現を照合し、必要に応じて具体シナリオや edge case で境界を明確化する。

### 非交渉制約

質問前シートに図を常に含めるのではなく、判断の構造や境界を理解しやすくする場合に含める、と明確化する。

### 受け入れ条件

`AC-001` に、用語衝突、曖昧語、責務境界の不一致を検出し、具体シナリオや edge case で確認することを追加する。

`AC-006` に、ADR candidate を sparingly に扱う条件を追加する。

### 用語

`TERM-002: 質問シート` の「図」を、必要に応じた図へ補正する。

## やりすぎた場合のリスク

- 用語 sharpening を強くしすぎると、すべての会話が用語レビューになり、clarification の速度が落ちる。
- 具体シナリオ / edge case を常時必須にすると、軽微な確認にも重い artifact が必要になる。
- ADR 条件を絶対化すると、spec-dock 側で必要な architecture decision の記録を逃す可能性がある。
- PlantUML を完全に任意化しすぎると、複雑な判断で図が省略されやすくなる。

## 採用判断

採用。

ただし、補正は requirement の既存構造を壊さない最小差分に留める。

## 人間への追加質問

なし。

今回の補正は、既存のユーザー回答と consultant review から十分に導ける。
