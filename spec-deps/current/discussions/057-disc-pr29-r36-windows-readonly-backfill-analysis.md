# 057-disc-pr29-r36-windows-readonly-backfill-analysis

## 概要

- 対象レビュー:
  - `P2 Handle readonly .meta.json files when backfilling on Windows`
- 対象コード:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - `write_meta()`
  - `backfill_github_repo_scope()`
- 対象 corrective scope:
  - `S03M readonly .meta.json backfill cross-platform contract`
  - 本 discussion は `S03L` 実装後に発見された Windows readonly backfill gap を `S03M` として継承した canonical analysis である

## 事実整理

- `write_meta()` は `.meta.json` 書き込み後に `_try_make_readonly()` を常に呼ぶ
  - `_try_make_readonly()` 自体は `chmod(mode & ~0o222)` を全 OS で実行し、`posix` 分岐は write bit が落ちたかの追加検証だけである
- `backfill_github_repo_scope()` は `.meta.json` を更新する前に writable 化するが、その処理と mode 復元を `os.name == "posix"` に限定している
- `backfill_github_repo_scope()` の実書き込みは `write_json()` 経由で `.meta.json` を再書き込みする
- 当時の `S03M` 分析時点では、`sync --github` の safe backfill は `collect_sync_state()` の途中で呼ばれ、`backfill_github_repo_scope()` の失敗は握りつぶされず sync failure になる
- この call path は後続 `S03N` / `S03O` で final contract から外れ、current state では bulk `sync --github` が legacy unscoped linkage を backfill しない non-mutating path へ整理されている
- 現行テストは readonly の `.meta.json` を Windows 相当契約のまま backfill するケースを固定していない

## 外部根拠

- Python `os.chmod()` 公式 docs:
  - Windows では read-only flag 以外の mode bits はほぼ無視され、実質的に read-only 制御に使われる
  - https://docs.python.org/3/library/os.html#os.chmod
- Microsoft file attribute docs:
  - `FILE_ATTRIBUTE_READONLY` は file が read-only であり、write/delete できないことを意味する
  - https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants

## 妥当性判定

### verdict

- このレビュー指摘は妥当である
- 修正は必要である

### 理由

- 現行コードは `.meta.json` の readonly 化を cross-platform に意図している一方、backfill 時の writable 化だけを `posix` 限定にしており、契約が非対称である
- そのため Windows では `write_meta()` で readonly 化された `.meta.json` を `backfill_github_repo_scope()` が再書き込みできず、`sync --github` の self-healing path が失敗しうる
- これは単なる warning surface の問題ではなく、`S03L` の no-origin continuity / safe backfill contract を一部環境で破る実害である

## 修正案比較シート

| 案 | 内容 | 利点 | 欠点 | 判定 |
|---|---|---|---|---|
| A | `backfill_github_repo_scope()` だけを最小修正し、Windows でも一時 writable 化と復元を行う | 差分が小さく hotfix として速い | readonly/writable 制御が `write_meta()` と `backfill` で分散したまま残り、同種 drift を再発しやすい | 可 |
| B | `.meta.json` 専用 helper を追加し、「一時 writable 化 -> write -> 元の lock 状態へ復元」を `write_meta()` と `backfill_github_repo_scope()` で共有する | 今回の root cause である permission 契約の重複実装 drift を解消できる。Windows/posix 両方で挙動を揃えやすい | A より少し変更範囲が広い | 最良 |
| C | temp file 書き込み + replace へ寄せる | 更新原子性を上げられる可能性がある | 今回の本質は readonly 制御であり、replace でも permission 前提は消えない。問題に対して過剰 | 非推奨 |

## 推奨方針

- 推奨は `B`

### 推奨理由

- 今回の不具合の根本は「Windows 非対応」そのものより、`.meta.json` の permission contract が `write_meta()` と `backfill_github_repo_scope()` に二重実装されて drift したことにある
- `B` なら `S03L` だけでなく今後の `.meta.json` mutation path でも同じ helper を再利用でき、review/QA の観点も明確になる
- helper は汎用 FS abstraction ではなく、`.meta.json` 専用の狭い責務に留めるのがよい

## 推奨修正の具体化

### 実装方針

- `infra/fs_repo.py` に `.meta.json` 専用 helper を追加する
  - 例:
    - 現在の mode / readonly 状態を取得する
    - 必要なら Windows / posix の両方で一時 writable 化する
    - write 実行後、final readonly lock state へ戻す
- `write_meta()` はこの helper を通して `.meta.json` を書き、その後の readonly 化を helper 内に寄せる
- `backfill_github_repo_scope()` も同じ helper を通して更新し、Windows でも readonly file を安全に backfill できるようにする
- restore 失敗時の warning policy は既存の `readonly_lock_failed` surface と整合させる

### 契約上の明文化ポイント

- successful create/backfill 後の final `.meta.json` lock state は `readonly` に揃える
- `write_meta()` と `backfill_github_repo_scope()` の両方が、成功時に same final readonly state を残すことを acceptance に含める
- relock/restore failure は metadata write 成功時でも silent success にせず、既存 `readonly_lock_failed` warning surface で観測できる契約とする

## 必要テスト

- provider-side:
  - readonly `.meta.json` を backfill して成功する regression
  - writable 化後に final readonly lock state が復元される regression
  - Windows 契約相当として `chmod` で write bit を戻した readonly file を backfill できる regression
  - relock/restore failure が `readonly_lock_failed` warning surface に載る regression
- parity:
  - checked-in runtime 側でも同じ readonly backfill regression を固定する
- negative:
  - conflicting existing scope / partial scope では従来どおり fail-closed を維持する

## 結論

- レビューは妥当
- 修正は必要
- 最良案は `.meta.json` の writable/readonly 制御を helper へ集約する `B`
