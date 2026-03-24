# 059-disc-pr29-r38-dead-sync-backfill-analysis

## metadata
- kind: discussion
- id: `059-disc-pr29-r38-dead-sync-backfill-analysis`
- issue: `issue-28-runtime-regression-bugs`
- scope: `S03O retire dead bulk sync backfill contract`
- related_review:
  - `P1 Pass trusted current-repo candidates into sync backfill`
- related_files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `spec-dock/scripts/spec_dock_runtime/application/repo_context.py`
  - `spec-dock/scripts/spec_dock_runtime/application/sync_state.py`
- status: `accepted`

## facts

- `collect_safe_current_repo_backfill_node_ids()` は unscoped node を current-repo candidate に入れる条件を `trusted_current_repo_node_ids` に限定した
- `collect_sync_state()` / `_apply_safe_current_repo_scope_backfill()` はその trusted set を一切渡していない
- その結果、bulk `sync --github` における legacy unscoped linkage の sync-time backfill path は到達不能になっている
- 現行 docs はなお「trusted context がある mutate-time backfill」と「AC-021 no-origin continuity」を live contract として残している
- `current_repo_slug` 単独、issue-number uniqueness、same-number foreign coexistence、current repo `issue_index()` の存在だけでは current repo 所属を positive に証明できず、trusted evidence にはならない

## analysis

- この review 指摘は妥当である
- 現状は docs drift ではなく、accepted された `AC-021` / `S03L` / `S03N` の一部実装が dead path 化している
- ただし bulk `sync --github` は target-less mutate path であり、現在の command contract のまま新しい trusted evidence を安全に生成する方法がない
- ここで ambient heuristic を trusted evidence とみなすと、`S03N` で止めた silent current-repo mis-normalization を再導入する
- よって current corrective scope では、bulk `sync --github` を trusted mutate-time backfill source と見なす契約自体を撤回し、write-time normalization と already-normalized metadata continuity を正本へ寄せるのが最も安全で整合的である

## options

| option | summary | pros | cons | verdict |
| --- | --- | --- | --- | --- |
| A | bulk `sync --github` の sync-time backfill contract を廃止し、docs/impl を write-time normalization 中心へ揃える | 安全性が最も高く、dead path を消せる。`S03N` の fail-closed を壊さない | legacy unscoped metadata の self-heal 範囲は縮む | 最良 |
| B | bulk sync の中で新しい trusted evidence を推定生成して backfill を復活させる | docs 上の self-heal 範囲を維持しやすい | `issue_index` や uniqueness を trust 扱いすると誤 backfill の再発リスクが高い | 不可 |
| C | docs だけ弱めて dead code は残す | 差分が小さい | dead path と誤解を残し続ける | 非推奨 |

## decision

- 採用案は `A`
- `AC-021` は「current repo slug を解決できる write path で explicit scope を保存し、その正規化済み metadata が no-origin 継続性を持つ」契約へ補正する
- bulk `sync --github` は legacy unscoped linkage を mutate しない
- legacy unscoped metadata の self-heal を再導入するなら、将来別 issue で explicit request intent または persisted provenance を trusted source とする新 contract を設計する

## concrete follow-up

- requirement/design/plan/report を `S03O` として更新する
- provider/check-in runtime から dead bulk sync backfill call path を除去する
- regression は次を固定する
  - bulk `sync --github` が lone unscoped legacy linkage を backfill しない
  - already-normalized metadata の no-origin continuity は維持される
  - write-time current-repo explicit scope persistence は維持される
  - provider/check-in parity で dead path が残らない
