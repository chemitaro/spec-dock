---
種別: discussion
ID: "021"
タイトル: "pr-29 review r5 active entrypoint rebuild analysis"
状態: "closed"
作成者: "Codex CLI"
作成日: "2026-03-19"
関連: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# pr-29 review r5 active entrypoint rebuild analysis

## 対象指摘

- review id:
  - `2957830289`
- path:
  - `src/spec_dock/cli.py:268`
- 要旨:
  - `spec-dock update` の active recovery は `context-pack.md` だけ persisted `.agent/active.json` を見て再生成するが、`spec-dock/active/{initiative,epic,issue}` 自体は placeholder に固定される
  - そのため active dir が消失した repo では、context-pack と実際の read path が食い違う

## 事実確認

- `_ensure_active_fallback_entrypoints()` は missing な active pointer に対して常に `_active_placeholder_dir(specdock_dir, layer)` を向ける
- 同関数で persisted active manifest を読むのは `context-pack.md` が欠けている時だけで、pointer target の再構築には使っていない
- 既存 test は:
  - active dir が空の時に placeholder を復旧すること
  - `context-pack.md` を persisted active manifest から再生成すること
  - symlink 失敗時に `.path` fallback を作ること
  - を固定している
- persisted active manifest を使って `active/initiative|epic|issue` 自体を実ノードへ戻す test は現状ない

## 妥当性評価

- verdict:
  - `valid`
- 理由:
  - `context-pack.md` が実 active ids を表示しているのに、主要 read path である `spec-dock/active/issue/*` が placeholder を向くのは operator を誤誘導する
  - `update` は recovery 導線として説明されているため、persisted active manifest が健全なら entrypoint まで戻す方が自然

## 修正要否

- 判定:
  - `修正が必要`
- 理由:
  - `AC-006 active pathway` の「未設定であることと次に取るべき path が分かる」に加えて、persisted active manifest が残っている場合は未設定扱いに戻してはいけない
  - 現状は recovery path と表示内容が不整合で、main read path が壊れたまま残る

## 修正案

### 案 A
- 内容:
  - `_ensure_active_fallback_entrypoints()` で persisted active ids を読み、対応 node path が repo 内に存在する場合は placeholder ではなくその node directory への symlink / `.path` を再構築する
  - `context-pack.md` も同じ persisted ids を使う
- 利点:
  - update recovery だけで active read path と context-pack を同時に整合させられる
  - runtime `active set` を再実行しなくても復旧できる
- 懸念:
  - installer 側で id -> path 解決ロジックを 1 つ持つ必要がある

### 案 B
- 内容:
  - active pointer は placeholder のままにし、`context-pack.md` も placeholder ベースへ戻して一貫性だけ守る
- 利点:
  - 変更量は小さい
- 懸念:
  - persisted active manifest があるのに recovery 効果を捨てることになる
  - 既に保存されている active state を update が活かせない

### 案 C
- 内容:
  - update では placeholder のみ復旧し、persisted active manifest が残っていた場合は warning を出して `active set` 再実行を要求する
- 利点:
  - 実装は比較的単純
- 懸念:
  - self-healing の価値が下がる
  - `context-pack.md` 再生成だけ成功する現状よりはましだが、導線として一段弱い

## 推奨案

- 推奨:
  - `案 A`
- 理由:
  - 既に persisted active manifest を読む基盤はあり、update recovery の期待値とも一致する
  - operator から見た primary path と summary path を同時に直せる
  - `active set` を再要求しないので、復旧体験が最も自然

## 実装時の注意

- persisted ids が存在しても、対応 path が repo 内に存在しない / kind が不一致なら placeholder に safely fall back する
- symlink 作成失敗時は既存どおり `.path` fallback を使う
- regression として次を固定する:
  - persisted active manifest があり active dir が空なら、`active/initiative|epic|issue` が実 node を向く
  - 対応 path 不在なら placeholder に fall back する
  - `context-pack.md` と active entrypoint が同じ active state を表す

## 結論

- review は `valid`
- 修正は `必要`
- 最良の修正方針は `persisted active manifest から active entrypoint 自体を再構築する`
