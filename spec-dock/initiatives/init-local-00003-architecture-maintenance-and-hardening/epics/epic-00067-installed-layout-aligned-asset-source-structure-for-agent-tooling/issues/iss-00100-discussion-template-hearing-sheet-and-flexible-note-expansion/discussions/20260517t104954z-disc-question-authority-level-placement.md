---
種別: disc
ID: "20260517t104954z-disc"
タイトル: "question authority level placement"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-05-17"
親: ["iss-00100"]
関連: ["#100", "20260517t103746z-disc"]
---

# 20260517t104954z-disc question authority level placement

## 質問
- authority level を、discussion doc の front matter に持たせるべきか。

## なぜ質問するのか
- authority level は、文書が「未整理メモ」「根拠」「提案」「決定済み正本」のどれに近いかを示す重要な情報である。
- これを front matter に持たせると、agent や tooling が検索、一覧、警告、反映判断に使いやすい。
- 一方で、全 artifact に必須 metadata を増やすと、作成負荷と validation 変更が増える。

## 背景
- discussion docs は、正本へ反映する前の情報を扱う作業面である。
- 未確定な `scratch` や `disc` が、誤って `adr` / `requirement` / `design` と同等に扱われると危険である。
- consultant の意見は、front matter 化推奨が優勢だった。
- ただし、初期実装では runtime 影響を抑えるため、本文 guidance に留める案もある。

## 事前分析

| 観点 | front matter に持つ | docs guidance に留める |
|---|---|---|
| agent の機械判定 | 強い | 弱い |
| validation / tests | 追加が必要 | 追加不要または軽い |
| 書く人の負荷 | やや増える | 低い |
| 将来の dashboard / search | 使いやすい | 本文解析が必要 |
| 誤用防止 | 強い | 人間の運用頼み |

## 回答案

### A: 必須 front matter として持つ
- 例:
  - `authority: raw | synthesized | proposed | accepted | superseded`
- 利点:
  - agent / tooling が確実に扱える。
  - 未確定情報を正本扱いする事故を減らせる。
- 懸念:
  - 既存 template と validation への影響が大きい。
  - 書く人が値選択で迷う可能性がある。

### B: doc type の既定値として扱い、front matter には持たない
- 例:
  - `scratch` は `raw`
  - `research` は `synthesized`
  - `disc` は `proposed`
  - `adr` は `accepted`
- 利点:
  - 作成負荷が低い。
  - 初期実装が軽い。
- 懸念:
  - 例外を表現しにくい。
  - agent が文書単位で authority を確認しにくい。

### C: doc type 既定値 + 例外時のみ front matter override
- 例:
  - 通常は type から推定する。
  - 例外だけ `authority: raw` などで明示する。
- 利点:
  - 作成負荷と機械可読性のバランスが良い。
  - 例外を表現できる。
- 懸念:
  - 「未指定時の既定値」を docs / runtime で明確にする必要がある。

## 推奨案
- 推奨は C。
- 初期実装では doc type ごとの既定 authority を docs と template guidance に明示し、必要に応じて front matter の `authority` で override できる形にする。
- 将来 dashboard / validation / search で authority を強く使う段階で、必須 front matter 化を検討する。

## ユーザー回答
- C を支持する。
- authority level は doc type の既定値を持ち、例外時だけ front matter で override できる設計にする。

## 回答欄
- 選択:
  - [ ] A: 必須 front matter として持つ
  - [ ] B: doc type の既定値として扱う
  - [x] C: doc type 既定値 + 例外時のみ override
- コメント:

## 回答後の反映先
- `requirement.md`
- `design.md`
- discussion template common metadata
- runtime validation scope
