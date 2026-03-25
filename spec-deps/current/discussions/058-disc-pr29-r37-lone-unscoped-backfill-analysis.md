# 058-disc-pr29-r37-lone-unscoped-backfill-analysis

## 概要

- 対象レビュー:
  - `P2 Avoid backfilling lone unscoped linkages as the current repo`
- 対象コード:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py`
  - `collect_safe_current_repo_backfill_node_ids()`
- 対象 corrective scope:
  - `S03N tighten safe backfill evidence for legacy unscoped linkage`
  - 本 discussion は `S03L` 実装後に判明した lone unscoped legacy linkage の silent current-repo backfill risk を扱う canonical analysis である

## 事実整理

- 現行 `collect_safe_current_repo_backfill_node_ids()` は `explicit_repo_slug or current_repo_slug` を effective repo scope として扱う
- そのため `github.repo_owner/name` が absent な lone unscoped legacy linkage は、同番号に partial scope や duplicate がなければ current repo candidate 1 件として eligible になりうる
- `sync --github` の mutate path は eligible node を silent に `repo_owner/name=current_repo_slug` へ書き戻す
- 現行 docs も同じ predicate を safe backfill として記述しており、コードと docs は現状整合している
- しかしこの predicate は「current repo と証明された」ではなく「current repo と仮定しても衝突しない」に留まる
- repo docs には「legacy unscoped foreign linkage は歴史的に存在しない」という保証はない

## 妥当性判定

### verdict

- このレビュー指摘は妥当である
- 修正は必要である

### 理由

- lone unscoped legacy linkage は repo scope を持たず、current repo slug と uniqueness だけでは current repo 所属を証明できない
- その状態で persisted metadata を current repo scope へ silent backfill するのは heuristic mutation であり、`safe backfill` と呼ぶには根拠が弱い
- 現行 design が掲げる `legacy unscoped current-repo linked node` と `no new heuristic` の方針とも緊張する

## 修正案比較シート

| 案 | 内容 | 利点 | 欠点 | 判定 |
|---|---|---|---|---|
| A | lone unscoped linkage は一律 backfill 禁止 | 最も安全。silent mis-normalization を止められる | no-origin continuity の回復範囲が縮む | 可 |
| B | positive current-repo evidence がある時だけ backfill 許可 | 安全性と運用性のバランスが最も良い。`safe` の意味を保てる | trusted context の定義を docs と tests で固定する必要がある | 最良 |
| C | 現行維持 | 既存 docs/tests 変更が最小 | silent fail-open mutation が残る。履歴保証がない限り unsafe | 非推奨 |

## 推奨方針

- 推奨は `B`

### 推奨理由

- persisted metadata mutation の根拠としては uniqueness-only heuristic は弱すぎる
- `safe backfill` は positive current-repo evidence がある場合に限定する方が、S03L の安全性主張と整合する
- bulk `sync --github` に限ると trusted context を持ちにくいため、実務上は `A` にかなり近い挙動になるが、それでも write-time normalization を維持できるぶん `B` の方が整理しやすい

## 推奨修正の具体化

### evidence contract

- positive current-repo evidence は、少なくとも次のような「current repo target intent が explicit な文脈」に限る
  - write-time create / import / link で current repo slug と target intent が同時に確定している場合
  - exact canonical current-repo target など、repo scope を明示した operator intent が command surface で渡る場合
- lone unscoped legacy linkage で repo scope を持たず、bulk `sync --github` のように explicit target context もない場合は backfill しない
- same-number foreign scoped coexistence は「backfill を妨げない」根拠にはならず、単独では positive evidence にならない

### expected behavior

- newly created/imported current-repo linkage は従来どおり write-time normalization で explicit scope を保存する
- legacy lone unscoped linkage は trusted context が無い限り fail-closed / manual remediation に残す
- no-origin continuity は「既に normalized された metadata」または「trusted context で safely normalized できた metadata」に対して保証する

## 必要テスト

- provider-side:
  - lone unscoped legacy linkage は bulk `sync --github` で current repo scope へ silent backfill されない regression
  - same-number foreign scoped coexistence があっても、それだけでは lone unscoped node を backfill しない regression
  - write-time current-repo create/import は従来どおり explicit scope persistence を維持する regression
- parity:
  - checked-in runtime 側でも lone unscoped no-backfill contract を固定する
- continuity:
  - already-normalized metadata の no-origin continuity regression は維持する

## 結論

- レビューは妥当
- 修正は必要
- 最良案は `positive current-repo evidence` がある場合だけ backfill を許可する `B`
