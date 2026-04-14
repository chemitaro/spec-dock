# Review Analysis E: top-level bot review body の扱い

- Source PR: `https://github.com/chemitaro/spec-dock/pull/73`
- Review source:
  - Copilot top-level review body
  - Codex top-level review body
- Analyst mode: main analysis + consultant second opinion

## Finding

top-level review body 自体が追加の actionable finding を持っているかを判定する必要がある。

## Evidence

- Copilot top-level review body は:
  - PR 概要
  - reviewed files summary
  - `generated 3 comments` というメタ情報
- Codex top-level review body は:
  - review boilerplate
  - reviewed commit 表示
  - inline suggestion があればそちらを見るべきという導線
- 固有の file/path/behavior を持つ actionable finding は inline comments に分離されている

## Assessment

- Validity: `妥当`
- Response priority: `不要`
- Why:
  - top-level body は triage 補助情報であり、個別対応すべき finding ではない
  - 実際の対応対象は A-D の inline/path-specific comments

## Options

### Option 1: top-level body も個別指摘として扱う

- Pros:
  - 取りこぼしを減らせる可能性がある
- Cons:
  - boilerplate に過剰反応しやすい
  - triage ノイズが増える

### Option 2: top-level body を完全に無視する

- Pros:
  - ノイズを減らせる
- Cons:
  - 将来 top-level に本物の finding が来た時に取りこぼす

### Option 3: file/path/behavior を伴う具体指摘がある場合のみ actionable と扱う

- Pros:
  - ノイズと見落としのバランスがよい
  - bot review 運用として現実的
- Cons:
  - 人手 triage は必要

## Best Response

`Option 3` が最善。

- top-level body はまずメタ情報として読む
- file/path/behavior/action request を持つ具体指摘がある場合のみ actionable 扱いにする
- 今回は actionable finding は A-D 側にのみ存在すると整理する

## Decision

- Classification: `対応不要`
- Action requirement: `no code/doc change required`

## Notes

consultant 評価でも E は triage policy の論点であり、今回 PR の修正対象ではないと判断された。
