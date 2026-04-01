# reference: GitHub（`gh` 連携）

このドキュメントは、spec-dock が GitHub CLI（`gh`）を使う箇所と、その前提/副作用/注意点をまとめた参照です。

関連:
- 入口: [README.md](README.md)
- 総合: [guide.md](guide.md)
- 命名: [reference_naming.md](reference_naming.md)

## 1. 前提（どのリポジトリが対象になるか）

spec-dock は `gh` の全コマンドで一律に `--repo owner/repo` を省略するわけではありません。  
`import` / `active set` / deps check / sync の `gh issue view` 系では repo slug が分かっている場合に `--repo owner/repo` を付け、same-repo URL import でも current repo を明示して読み取ります。  
一方で `gh issue create` / `gh issue list` は repo root を `cwd` にして実行し、対象リポジトリ解決は **`gh` の通常解釈**に委ねます。

補足:
- `spec-dock update` は managed files/docs/templates/scripts/skills を refresh しますが、old workspace の in-place migration は保証しません
- legacy `meta.json`、partial linkage、current-repo mismatch などの old contract 不整合は、`update` で吸収されず current create / import / validate / sync が reject / fail-fast しうります
- その場合は auto-migrate を期待せず、手動で normalize するか workspace を rebuild してください

代表的な解決材料（`gh` 側）:
- カレントディレクトリが Git リポジトリであること
- `git remote` の URL
- 必要に応じて `GH_REPO` 等の環境変数
- `gh auth`（認証）状態

## 2. 何が GitHub を更新し、何が読み取りだけか

### 更新する（GitHub Issue を作成する）

- `new initiative` / `new epic` / `new issue`（デフォルト）は GitHub Issue を作ります（`gh issue create`）
  - `--create-github-issue` は同じ意味の explicit alias です
  - `initiative / epic / issue` では GitHub linkage が mandatory です
  - `--no-github` は compatibility option として残っていますが、contract error で reject されます

### 読み取りだけ（非交渉）

- `import {initiative,epic,issue}` は **読み取りのみ**です
  - `gh issue view` で存在確認するだけで、GitHub の Issue 本体（title/body/labels 等）を更新しません
  - `--title` は必須です（GitHub title は取り込みません）
  - ローカルにはノードを生成し、`sync --no-update-active` 相当まで実行します（active は変更しません）
  - `import` は実行前に preflight validate（`validate` 相当）を行い、既存ツリーが不整合な場合は **副作用（テンプレートコピー/`.meta.json`生成）なし**で失敗します
  - `meta.json`（レガシー名）が混在しているツリーは非対応です（`.meta.json` へ手動移行後に実行してください）
  - linkage mismatch / current-repo mismatch は手動 normalize 前提で reject され、auto-repair / auto-migrate は行いません

### GitHub を呼ばない（ローカルのみ）

- `new {initiative,epic,issue} --github-issue <n>` は「既存番号へリンク」するだけで、GitHub Issue は作りません（`gh` を呼びません）
- 生成される `epics/rules.md` / `issues/rules.md` / `discussions/rules.md` は `spec-dock/docs/rules/**` への symlink です。`rules.md` は入口/ナビゲーション用で、ルールの正本は `spec-dock/docs/rules/**` にあります。runtime command はサポートされた実行経路です

## 3. `import` の URL 入力に関する注意（事故防止）

`import` は `123` / `#123` / canonical GitHub issue URL を受け付けます。

重要:
- canonical URL は `https://github.com/<owner>/<repo>/issues/<n>` の形だけを受け付けます
- `import` は URL 内の `owner/repo` を current repo（`git remote.origin.url`）と照合します
- `owner/repo` mismatch は reject されます
- `initiative / epic / issue` node import は single-repo / GitHub-backed identity contract のため、foreign issue URL を許可しません
- `--allow-foreign-url` は compatibility flag として残っていますが、node identity import の成功経路にはなりません
- canonical でない URL-like target（例: `git@github.com:owner/repo/issues/123`）は reject します
- current repo を検証できない場合（origin 未設定 / GitHub 以外の remote）は、canonical URL import を fail-closed で reject します

## 4. `active set` と checkout（安全装置）

`active set` は target を active として固定します。

- デフォルトは **no-checkout**（active 更新のみ）です
- 後方互換として `active set <target>` は維持されます
- explicit form として `active set --id <node-id>` / `active set --github-issue <n>` も使えます
- checkout は `active set <target> --checkout` を明示したときだけ実行します
- target 解決はローカル node（`.meta.json`）を優先し、未解決なら checkout/active 変更なしで失敗します
- `--checkout` 時に作業ツリーが dirty の場合は安全のため checkout を中断します
- `--checkout` を伴う場合、ブランチ名は `<id>-<slug>`（不適合なら `<id>`）へ正規化されます（非ASCIIブランチ名を避ける）。詳細は [reference_naming.md](reference_naming.md) を参照してください。

## 5. `github.issue_number` のリンクと一意性（重要）

`github.issue_number` は、node（initiative/epic/issue）を GitHub Issue 番号へ紐づけるためのメタデータです。

- `new issue`（デフォルト）: `gh issue create` の結果（Issue番号）でリンクします
- `new issue --create-github-issue`: デフォルトと同じく `gh issue create` の結果（Issue番号）でリンクします
- `new {initiative,epic,issue} --github-issue <n>`: 既存番号へリンクします（新規 Issue は作りません）
- `new initiative --create-github-issue` / `new epic --create-github-issue`: `gh issue create` の結果（Issue番号）でリンクします
- `import <n|#n|url>`: 既存番号へリンクします（読み取り確認のみ）

制約:
- **同じ `github.issue_number` を持つ node は、ツリー全体で 1つ**である必要があります（initiative/epic/issue をまたいで一意）。
  - 重複すると `active set <n|url>` が `Ambiguous github.issue_number=...` で失敗し得ます
  - `validate` / `sync` の preflight validate でも重複は検知され、エラーになります

重複が検出された場合（復旧）:
- エラーメッセージに `type:id (.meta.json path)` の競合一覧が出るので、どれか1つだけが `github.issue_number` を保持するように `.meta.json` を修正してください（他は削除/変更）
- 修正後に `./spec-dock/scripts/spec-dock validate` / `./spec-dock/scripts/spec-dock sync` を再実行してください

## 6. よくある失敗

- `gh` が未導入/未認証で `new issue`（デフォルト）が失敗する
  - `initiative / epic / issue` では GitHub linkage が mandatory なので、`gh auth login` 等を先に行ってください
- Epic 配下で local-only issue を作りたい
  - 現行 contract では `initiative / epic / issue` の local-only create はサポートされません
  - current repo の GitHub Issue を作るか、既存 current-repo issue に `--github-issue <n>` でリンクしてください
- canonical URL import が失敗する → current repo（`origin`）を検証できないか、`owner/repo` mismatch の可能性があります
  - foreign GitHub issue URL は node identity import として reject されます
  - `--allow-foreign-url` を付けても cross-repo node import の compatibility success path にはなりません
  - canonical でない URL-like target は受け付けません
