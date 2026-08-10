# 文書入口（spec-dock docs）

## Authoring Kit

Initiative / Epic / Issue の仕様を Markdown で作成・更新する場合は、まず [Authoring Kit 概要](authoring/overview.md) を参照してください。文書の責務、scope の境界、どこへ判断を残すかを説明します。この入口は特定の agent、provider、workflow の利用を必須にしません。

このディレクトリは `spec-dock init/update` により導入先リポジトリへ配置されます。  
仕様作成の first-read は Authoring Kit です。以下の workflow、phase、skill は既存 runtime や移行の詳細を確認するための任意リファレンスであり、Current Authoring Kit の必須手順ではありません。
Core runtime command の現行 contract は `./spec-dock/scripts/spec-dock ...`、Issue Planning command の現行 contract は `./spec-dock/scripts/spec-dock-chatgpt ...` です。これらの command reference は Authoring Kit の文書責務を置き換えません。

## 既存の agent / workflow リファレンス

`spec-dock init/update` は次の skill を導入します。これらは既存の agent 運用で参照できる詳細であり、仕様作成の開始条件や Current Authoring Kit の必須契約ではありません。

- Hub: `.agents/skills/spec-dock-hub/SKILL.md`
- Clarification: `.agents/skills/spec-dock-clarification/SKILL.md`
- Initiative: `.agents/skills/spec-dock-initiative-planning/SKILL.md`
- Epic planning: `.agents/skills/spec-dock-epic-planning/SKILL.md`
- Epic execution: `.agents/skills/spec-dock-epic-execution/SKILL.md`
- Issue planning: `.agents/skills/spec-dock-issue-planning/SKILL.md`
- Issue execution: `.agents/skills/spec-dock-issue-execution/SKILL.md`
- ChatGPT authoring evidence lane: `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
- Manual planning backups: `.agents/skills/spec-dock-initiative-planning-manual/SKILL.md`, `.agents/skills/spec-dock-epic-planning-manual/SKILL.md`, `.agents/skills/spec-dock-issue-planning-manual/SKILL.md`
- ADR: `.agents/skills/spec-dock-adr-facilitation/SKILL.md`

## Authoring Kit の後に参照できる既存資料

1. [guide.md](guide.md)
2. 必要に応じた対象 scope の workflow
   - [workflow_spec_authoring.md](workflow_spec_authoring.md)
   - [workflow_clarification.md](workflow_clarification.md)
   - [workflow_initiative.md](workflow_initiative.md)
   - [workflow_epic.md](workflow_epic.md)
   - [workflow_issue.md](workflow_issue.md)
   - [workflow_adr.md](workflow_adr.md)
3. phase の shared playbook
   - [phase_requirement.md](phase_requirement.md)
   - [phase_design.md](phase_design.md)
   - [phase_plan.md](phase_plan.md)
4. scope 固有の plan playbook
   - [phase_plan_initiative.md](phase_plan_initiative.md)
   - [phase_plan_epic.md](phase_plan_epic.md)
   - [phase_plan_issue.md](phase_plan_issue.md)
5. reference レイヤ
   - [reference_github.md](reference_github.md)
   - [reference_naming.md](reference_naming.md)
   - [reference_deps.md](reference_deps.md)
   - [reference_sync.md](reference_sync.md)
   - [workflow_chatgpt_authoring_pack.md](workflow_chatgpt_authoring_pack.md)
   - [reference_authoring_pack_backend.md](reference_authoring_pack_backend.md)
   - [authoring/chatgpt-pack.md](authoring/chatgpt-pack.md)

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

# 既存 Issue Planning command reference（外部 output directory を使う）
./spec-dock/scripts/spec-dock-chatgpt planning create --issue <issue-id> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt review planning --issue <issue-id> --mode archive-candidate --candidate <candidate.zip> --output <external-review-dir>
./spec-dock/scripts/spec-dock-chatgpt review planning --issue <issue-id> --mode git-bound --candidate <candidate.zip> --reviewed-head <sha> --output <external-review-dir>
./spec-dock/scripts/spec-dock-chatgpt planning revise --candidate <candidate.zip> --request <external-review-dir>/planning-revision-request.json --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt planning apply --issue <issue-id> --mode archive-candidate --review-result <review.json> --human-decision <decision.json> --expected-head <sha> --output <external-dir> --candidate <candidate.zip> --logical-filename <name> --zip-sha256 <sha256>
./spec-dock/scripts/spec-dock-chatgpt planning apply --issue <issue-id> --mode git-bound --review-result <review.json> --human-decision <decision.json> --expected-head <sha> --output <external-dir> --candidate <candidate.zip> --reviewed-head <sha>

./spec-dock/scripts/spec-dock active set <id|#num|url>
./spec-dock/scripts/spec-dock active set --id <node-id>
./spec-dock/scripts/spec-dock active set --github-issue <n>
./spec-dock/scripts/spec-dock active set <id|#num|url> --checkout
./spec-dock/scripts/spec-dock active show

./spec-dock/scripts/spec-dock deps check <target>
./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync

# experimental: one-shot scoped Workbench copy
./spec-dock/scripts/spec-dock workbench copy --scope <initiative|epic|issue-id> --to <linked-worktree>

# specialized Workbench Markdown evidence import
./spec-dock/scripts/spec-dock artifact import chatgpt-output --issue <issue-id> --file <workbench-file.md> --title "..."

# generic opaque evidence import: one explicit regular file, no Workbench requirement
./spec-dock/scripts/spec-dock artifact import file --root --file <path>
./spec-dock/scripts/spec-dock artifact import file --initiative <initiative-id> --file <path>
./spec-dock/scripts/spec-dock artifact import file --epic <epic-id> --file <path>
./spec-dock/scripts/spec-dock artifact import file --issue <issue-id> --file <path> [--json]

# 管理対象 files/docs/templates/scripts/skills の更新（refresh）
./spec-dock/scripts/spec-dock update
./spec-dock/scripts/spec-dock update /path/to/project
```

## 高頻度ルール

- Initiative / Epic は `new` / `import` の前に既存ノード再利用を確認する
- Requirement / design / plan の文書責務は [Authoring Kit 概要](authoring/overview.md) を参照する。既存 planning skill や workflow は、必要な場合にだけ追加の運用リファレンスとして使う
- ChatGPT / Oracle を使う場合の既存 evidence lane は [workflow_chatgpt_authoring_pack.md](workflow_chatgpt_authoring_pack.md) に記録されている。これは Current Authoring Kit の正規 route や必須手順ではなく、出力は evidence-only である
- Issue Planning command の既存実行依存と制約は repo-local `./spec-dock/scripts/spec-dock-chatgpt` の reference として保持する。Current Authoring Kit の仕様作成はこの command を前提にしない
- Planner と Semantic Revision は canonical `requirement.md` / `design.md` / `plan.md` と runtime-selected の exactly-one onboarding companion を含む exactly-one authoring ZIP を返し、Reviewer は closed JSON を返す。companion は第四のcanonical specificationではなく subordinate evidence である
- `planning revise`、Review/apply、manual backup、clarification、phase playbook の記述は既存 workflow reference として保持する。Current Authoring Kit の仕様作成に特定の provider、review、phase 順序を必須化しない
- `new initiative` / `new epic` / `new issue` はデフォルトで GitHub Issue を作る。node create/import で local-only create へ自動フォールバックしない
- `new issue --create-github-issue` は default create の explicit alias
- node creation で既存 Issue へ紐づける場合は `--github-issue <n>` を使う。`--no-github` は node creation option ではない
- `--allow-foreign-url` は compatibility flag として残るが、current contract mismatch を auto-migrate せず reject/fail-fast しうる
- `import` は読み取り確認のみで、GitHub を更新しない。canonical URL は current repo と照合し、cross-repo node import は reject される
- Issue 実行の通常入口は `issue start <target>`、終了導線は `issue finish`。`active set` / `active set --checkout` は manual / recovery 用の low-level command として使う
- `active set` / `deps check` は `<target>` の後方互換を維持しつつ、`--id` / `--github-issue` の explicit form も使える
- 依存関係の追加/削除/確認は metadata の直編集ではなく `./spec-dock/scripts/spec-dock deps add/remove/check` を使い、変更後は `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` で GitHub live state を含めて整合を確認する。GitHub を呼ばない確認が必要な場合だけ `--no-github` を指定する
- legacy sequential discussion docs は grandfathered only。新規作成で sequence reuse / auto-rename / auto-repair はしない
- `./spec-dock/scripts/spec-dock update [path]` は repo-local self-update path で、target 省略時は current directory を更新する。明示 path を渡すとその managed repo を更新する
- runtime update は installer update の wrapper であり、固定 upstream `git+https://github.com/chemitaro/spec-dock` を `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>` として実行する。arbitrary source / cache / `--force` option は公開しない
- update は managed files/docs/templates/scripts/skills の更新であり、`init --force` でも old workspace の in-place migration ツールでもない。current contract mismatch は手動 normalize / rebuild が必要な場合がある
- Workbench は任意です。optional、temporary、worktree-local、disposable、non-canonical な作業場であり、fresh root と future Initiative / Epic / Issue の shell に `.workbench/README.md` が生成されますが、existing scope には no-backfill です。presence は任意であり、不在でも workspace は valid です
- `.workbench/README.md` は direct child の README-only tracking surface です。その他の Workbench entry は ignored payload として Git に ignore されます。Git ignore は security boundary ではありません。secret、credential、private customer data を置かないでください
- Workbench content の read / import authorization は evidence-only であり、canonical adoption ではありません。`artifact import chatgpt-output` は approved Workbench の単一 Markdown を source/bytes 不変で blank Artifact へ copy する実装済み specialized lane です。`chatgpt-output` typed token は予約せず、`new artifact` と共存します。imported ChatGPT output は evidence-only であり、canonical 採用には Evidence Adoption Ledger の採否、canonical docs への再記述、fresh reviewer gate が必要です
- `artifact import file` は Workbench と `chatgpt-output` から独立した generic lane です。`--root` / `--initiative` / `--epic` / `--issue` のいずれか一つと `--file` を指定し、一件の明示 regular file を opaque generic Artifact として保存します。source は変更・削除しません。generic result は source content、hash、byte count、repository 外 absolute path を出さず、repository 内 source は repo-relative、その他は basename のみを表示します
- generic import の成功は `committed=true` です。`publication_state=committed` または commit 後 warning の `committed_with_warning` は `retry_disposition=not_needed`、commit 前 failure は `not_committed` と `safe_after_remediation` です。保存した generic Artifact は常に `canonical=false` であり、Evidence Adoption Ledger、canonical docs、accepted ADR、fresh reviewer gate を経ない自動採用はしません。filename と collision は [reference_naming.md](reference_naming.md)、scope ごとの利用ルールは対象 `artifacts/rules.md` を参照してください
- explicit generic import の publication は platform safety boundary を持ちます。Linux は anonymous `O_TMPFILE` staging を使い、named-temp success fallback を持ちません。macOS は destination-side named stage と検証済み staged descriptor からの `fclonefileat` no-replace publication を使い、commit 後 cleanup の不確実性は unsafe unlink ではなく warning になります。same-UID actor が final check と unlink の間に置換する事象は accepted exclusion のままです。詳細は [guide.md](guide.md) を参照してください
- ordinary `uv run pytest` は default full-regression skip を適用する fast lane です。full-regression body は別の explicit lane であり、`uv run pytest --run-full-regression` を実行します
- root `spec-dock/.workbench/` は日付 bucket と必要 file の手動選択だけを使い、root 一括 copy command は持ちません。Initiative / Epic / Issue scope の copy は、同一 repository の linked worktree へ明示実行する source-wins の one-shot copy であり、自動 sync も copy-back も行いません。Workbench copy は directory をそのまま扱い、言語、拡張子、MIME、内容による file classifier を持ちません。update は既存 Workbench を unmanaged local content として保持し、migration、normalize、delete、promotion しません
- Issue plan の既存 runtime / execution detail は `workflow_issue.md` に残るが、Current Authoring Kit の Plan 基礎契約は [Issue Plan Guide](authoring/issue-plan.md) を参照する
- naming 制約、GitHub 副作用、deps / sync の詳細は `reference_*.md` を参照する
