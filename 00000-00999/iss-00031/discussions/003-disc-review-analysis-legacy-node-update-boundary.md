# 003-disc-review-analysis-legacy-node-update-boundary

## 対象指摘
- 指摘:
  - `update` が legacy node tree を触らないという out-of-scope 境界を test で固定できていない。
- 参照:
  - `tests/test_init_update.py`
  - `spec-dock/active/issue/requirement.md`

## 結論
- 妥当性:
  - 妥当
- 修正必要性:
  - 中〜高
- 推奨:
  - `update` 実行前に既存 node 配下へ legacy artifact を植えた fixture を作り、それが preserve されることを 1 本の dedicated test で固定する。

## 妥当性の分析
- 今回の requirement では、既存 checked-in node 配下の wrapper / rules 実体置換は out of scope と明記されている。
- これは「直さない」こと自体が契約であり、実装がそこを越境しないことを確認する価値がある。
- 現状の update tests は template asset と docs/rules 配布面をよく押さえているが、「既存 node tree には手を入れない」という否定条件までは直接検証していない。
- 将来 broad cleanup が `spec-dock/templates/**` から `spec-dock/initiatives/**` 側へ広がると、この issue のスコープ逸脱が静かに混入する可能性がある。

## いま修正すべきか
- できれば今回か、少なくとも近い後続で修正した方がよい。
- 理由:
  - これは単なる追加安心材料ではなく、「この issue が何をしないか」の境界を守る test だから。
  - 仕様の非スコープは、実装者が変わるほど忘れられやすい。
  - 一方で release blocker 級ではないので、P2 として後続短期フォローアップに分ける判断も許容できる。

## 修正案

### 案A
- `tests/test_init_update.py` に dedicated test を追加する。
- 内容:
  - `init` 後に `spec-dock/initiatives/.../epics/new-epic` や node-local `discussions/rules.md` 実体など legacy artifact を fixture として配置する。
  - `update` 後もその artifact が残ることを assert する。
  - 同時に `templates/**` 側の legacy artifact は prune されることと対比で示す。
- 利点:
  - 要件境界をそのまま executable contract にできる。
  - `update` regression suite の責務に自然に収まる。
- 欠点:
  - fixture 準備がやや冗長になる。

### 案B
- 既存の `test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set` に assertion を継ぎ足す。
- 利点:
  - test 数が増えない。
- 欠点:
  - test の責務が広がりすぎる。
  - failure 時に何の契約が壊れたのか分かりにくい。

### 案C
- requirement/design/report に「legacy node preserve」をさらに明文化し、test は追加しない。
- 利点:
  - 文書だけなら最小。
- 欠点:
  - 既に文書上は明確なので、追加価値が低い。
  - 実行可能な guard にならない。

## 採用方針
- 案A が最も良い。
- 理由:
  - 非スコープ境界を test で守る、というこの指摘の本質に最短で応える。
  - future broad cleanup に対する safety rail として分かりやすい。

## 推奨する具体修正
- fixture は 1 つの initiative node に限定してよい。
- 残す対象は 2 つ程度で十分。
  - legacy `new-epic`
  - node-local `discussions/rules.md` 実体
- 対比として同一 test 内で次も押さえる。
  - `templates/**` 側の legacy artifact は update で除去される
  - node-local artifact は preserve される
- これで「どこは更新対象で、どこは非対象か」が一目で分かる。

## 見送る場合の判断
- 見送り自体は可能だが、close 前に follow-up issue として明示化した方がよい。
- 見送る場合の理由は「現状 implementation が requirement を破っているから」ではなく、「境界保護を test へ昇格しきれていないから」である。
