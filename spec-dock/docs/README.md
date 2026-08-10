# 文書入口（spec-dock docs）

このディレクトリは `spec-dock init/update` により導入先リポジトリへ配置されます。
この README は Storage Core Runtime のコマンド参照です。Current contract は `./spec-dock/scripts/spec-dock ...` です。

関連する Runtime reference:

- [reference_github.md](reference_github.md)
- [reference_naming.md](reference_naming.md)
- [reference_deps.md](reference_deps.md)
- [reference_sync.md](reference_sync.md)
- [reference_worktree.md](reference_worktree.md)

## 最短コマンド

```bash
./spec-dock/scripts/spec-dock new initiative --title "..."
./spec-dock/scripts/spec-dock new epic --initiative <initiative-id> --title "..."
./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title "..."
./spec-dock/scripts/spec-dock new issue --create-github-issue --epic <epic-id> --title "..."

./spec-dock/scripts/spec-dock import epic <num-or-canonical-url> --title "..." [--initiative <id>] [--allow-foreign-url]
./spec-dock/scripts/spec-dock import issue <num-or-canonical-url> --title "..." [--epic <id>] [--allow-foreign-url]

./spec-dock/scripts/spec-dock issue start <github-issue-number>
./spec-dock/scripts/spec-dock issue start --id <issue-id>
./spec-dock/scripts/spec-dock issue finish

./spec-dock/scripts/spec-dock active set <id|#num|url>
./spec-dock/scripts/spec-dock active set --id <node-id>
./spec-dock/scripts/spec-dock active set --github-issue <n>
./spec-dock/scripts/spec-dock active show
./spec-dock/scripts/spec-dock active clear

./spec-dock/scripts/spec-dock new artifact --issue <issue-id> --title "..." [blank|research|interview|disc|decision-candidate|adr]

./spec-dock/scripts/spec-dock deps check <target>
./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync

# experimental: one-shot scoped Workbench copy
./spec-dock/scripts/spec-dock workbench copy --scope <initiative|epic|issue-id> --to <linked-worktree>

# generic opaque evidence import: one explicit regular file, no Workbench requirement
./spec-dock/scripts/spec-dock artifact import file --root --file <path>
./spec-dock/scripts/spec-dock artifact import file --initiative <initiative-id> --file <path>
./spec-dock/scripts/spec-dock artifact import file --epic <epic-id> --file <path>
./spec-dock/scripts/spec-dock artifact import file --issue <issue-id> --file <path> [--json]

# 管理対象 files/docs/templates/scripts/skills の更新（refresh）
./spec-dock/scripts/spec-dock update
./spec-dock/scripts/spec-dock update /path/to/project
```

`spec-dock-chatgpt` は Storage Core Runtime 外の、後続Issueが所有する compatibility / handoff surface です。この README はその workflow や reviewer gate を Current の通常操作としては説明しません。

## Storage Core の運用ルール

- Initiative / Epic は `new` / `import` の前に既存ノード再利用を確認する
- `new initiative` / `new epic` / `new issue` はデフォルトで GitHub Issue を作る。node create/import で local-only create へ自動フォールバックしない
- `new issue --create-github-issue` は default create の explicit alias
- node creation で既存 Issue へ紐づける場合は `--github-issue <n>` を使う。`--no-github` は node creation option ではない
- `--allow-foreign-url` は compatibility flag として残るが、current contract mismatch を auto-migrate せず reject/fail-fast しうる
- `import` は読み取り確認のみで、GitHub を更新しない。canonical URL は current repo と照合し、cross-repo node import は reject される
- Issue 実行の通常入口は `issue start <target>`、終了導線は `issue finish`。`issue start` は dependency readiness を確認して branch checkout、active 設定、post-sync を行う。`active set` / `show` / `clear` は selection-only の構造操作で、checkout、GitHub 照会、dependency 判定を行わない
- `active set` / `deps check` は `<target>` の後方互換を維持しつつ、`--id` / `--github-issue` の explicit form も使える
- 依存関係の追加/削除/確認は metadata の直編集ではなく `./spec-dock/scripts/spec-dock deps add/remove/check` を使い、変更後は `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` で GitHub live state を含めて整合を確認する。GitHub を呼ばない確認が必要な場合だけ `--no-github` を指定する
- legacy sequential discussion docs は grandfathered only。新規作成で sequence reuse / auto-rename / auto-repair はしない
- `./spec-dock/scripts/spec-dock update [path]` は repo-local self-update path で、target 省略時は current directory を更新する。明示 path を渡すとその managed repo を更新する
- runtime update は installer update の wrapper であり、固定 upstream `git+https://github.com/chemitaro/spec-dock` を `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>` として実行する。arbitrary source / cache / `--force` option は公開しない
- update は managed files/docs/templates/scripts/skills の更新であり、`init --force` でも old workspace の in-place migration ツールでもない。current contract mismatch は手動 normalize / rebuild が必要な場合がある
- Workbench は任意です。optional、temporary、worktree-local、disposable、non-canonical な作業場であり、fresh root と future Initiative / Epic / Issue の shell に `.workbench/README.md` が生成されますが、existing scope には no-backfill です。presence は任意であり、不在でも workspace は valid です
- `.workbench/README.md` は direct child の README-only tracking surface です。その他の Workbench entry は ignored payload として Git に ignore されます。Git ignore は security boundary ではありません。secret、credential、private customer data を置かないでください
- `artifact import file` は唯一の Current import surface です。`--root` / `--initiative` / `--epic` / `--issue` のいずれか一つと `--file` を指定し、一件の明示 regular file を opaque generic Artifact として保存します。source は変更・削除せず、source content、hash、byte count、repository 外 absolute path は出力しません。既存の `artifact import chatgpt-output` は撤去済みで、同じ一件の file は `artifact import file` へ移行してください。filename と collision は [reference_naming.md](reference_naming.md) を参照してください
- explicit generic import の publication は platform safety boundary を持ちます。commit 前の failure は destination に公開せず、commit 後 cleanup の不確実性は unsafe unlink ではなく warning として扱います。
- ordinary `uv run pytest` は default full-regression skip を適用する fast lane です。full-regression body は別の explicit lane であり、`uv run pytest --run-full-regression` を実行します
- root `spec-dock/.workbench/` は日付 bucket と必要 file の手動選択だけを使い、root 一括 copy command は持ちません。Initiative / Epic / Issue scope の copy は、同一 repository の linked worktree へ明示実行する source-wins の one-shot copy であり、自動 sync も copy-back も行いません。Workbench copy は directory をそのまま扱い、言語、拡張子、MIME、内容による file classifier を持ちません。update は既存 Workbench を unmanaged local content として保持し、migration、normalize、delete、promotion しません
- naming 制約、GitHub 副作用、deps / sync の詳細は `reference_*.md` を参照する
