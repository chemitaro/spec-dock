# タイトル: "PR29 R35 persisted active path id trust analysis"

## 背景

- 2026-03-23 22:48:33 UTC の Codex review で、`src/spec_dock/cli.py` の active recovery が persisted manifest の `path` を same-layer prefix だけで信用し、wrong node へ repoint しうるという指摘が追加された
- ローカル再現では、`issue.id=iss-local-99999` と `path=.../iss-local-00002-*` を持つ stale manifest に対し `spec-dock update` が `iss-local-00002` を active issue として復旧した

## 観測事実

- `_resolve_manifest_target_dir()` は `expected_id` / `type` 一致を確認しているため、wrong-id path を直接は採用しない
- ただし、その後の `_resolve_persisted_path_dir()` は repo 内 / same-layer prefix / is_dir だけを見て `Path` を返すため、same-layer wrong-id node を fallback target として採用してしまう
- その結果、id authority は stale manifest にありながら、path hint が wrong node を勝ってしまう

## 問題

- active recovery の authority 順が逆転している
- persisted manifest の `id` が stale / broken でも、たまたま same-layer の実在 path なら誤復旧するため fail-closed にならない
- `context-pack.md` と `spec-dock/active/*` が wrong node を main read path として露出し、operator が silent corruption と区別しづらい

## 方針候補

### A. persisted path fallback にも `id` / `type` 一致を要求する

- 内容:
  - `_resolve_persisted_path_dir()` を `expected_id` aware にし、`.meta.json` の `id` / `type` が一致した時だけ recovery target として返す
- 長所:
  - authority が一貫する
  - same-layer wrong-id node を fail-closed に倒せる
  - 既存の valid persisted path recovery は維持しやすい
- 短所:
  - `.meta.json` 依存が増えるが、active entrypoint recovery 自体が node metadata 前提なので不自然ではない

### B. persisted path fallback 自体を廃止し、id-based recovery のみ許す

- 内容:
  - persisted path を一切信用せず、常に `expected_id` 探索か placeholder fallback のみで復旧する
- 長所:
  - authority が明快
- 短所:
  - valid persisted path があっても常に探索コストへ寄る
  - 現行 recovery の一部を unnecessary に弱める

## 採用方針

- A を採用する
- `path` は hint だが、hint を使う場合も `expected_id` / `type` 一致が必須
- 一致しない stale path は `None` を返し、既存の id-based recovery または placeholder fallback へ流す

## 受け入れ観点

- same-layer wrong-id persisted path は wrong node を active target にしない
- valid persisted path は既存どおり復旧できる
- healthy active entrypoint を stale manifest で上書きしない既存 contract を壊さない
