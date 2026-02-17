# reference: GitHub（`gh` 連携）

このドキュメントは、spec-dock が GitHub CLI（`gh`）を使う箇所と、その前提/副作用/注意点をまとめた参照です。

関連:
- 入口: [README.md](README.md)
- 総合: [guide.md](guide.md)
- 命名: [reference_naming.md](reference_naming.md)

## 1. 前提（どのリポジトリが対象になるか）

spec-dock は `gh` 実行時に `--repo owner/repo` を指定しません。  
そのため、対象リポジトリは **`gh` の解釈**で決まります。

代表的な解決材料（`gh` 側）:
- カレントディレクトリが Git リポジトリであること
- `git remote` の URL
- 必要に応じて `GH_REPO` 等の環境変数
- `gh auth`（認証）状態

## 2. 何が GitHub を更新し、何が読み取りだけか

### 更新する（デフォルト動作）

- `new {initiative,epic,issue}`（デフォルト）は GitHub Issue を作ります
  - GitHub を使わない場合は `--no-github` を付けてください（`gh` を呼びません）

### 読み取りだけ（非交渉）

- `import {initiative,epic,issue}` は **読み取りのみ**です
  - `gh issue view` で存在確認するだけで、GitHub の Issue 本体（title/body/labels 等）を更新しません
  - `--title` は必須です（GitHub title は取り込みません）
  - ローカルにはノードを生成し、`sync --no-update-active` 相当まで実行します（active は変更しません）
  - `import` は実行前に preflight validate（`validate` 相当）を行い、既存ツリーが不整合な場合は **副作用（テンプレートコピー/`meta.json`生成）なし**で失敗します

## 3. `import` の URL 入力に関する注意（事故防止）

`import` は `123` / `#123` / URL を受け付けますが、URL は **番号抽出のためだけ**に使います。

重要:
- URL 内の `owner/repo` は **無視**されます
- そのため、別リポジトリの URL を貼っても「現在の `gh` が見ているリポジトリの同番号 Issue」として解釈され得ます

クロスリポジトリ対応はスキーマ拡張や安全装置が必要になるため、別案件（別ADR）です。

## 4. `active set` と checkout（安全装置）

`active set` は target を active として固定します。

- デフォルトは **no-checkout**（active 更新のみ）です
- checkout は `active set <target> --checkout` を明示したときだけ実行します
- target 解決はローカル node（`meta.json`）を優先し、未解決なら checkout/active 変更なしで失敗します
- `--checkout` 時に作業ツリーが dirty の場合は安全のため checkout を中断します
- `--checkout` を伴う場合、ブランチ名は `<id>-<slug>`（不適合なら `<id>`）へ正規化されます（非ASCIIブランチ名を避ける）。詳細は [reference_naming.md](reference_naming.md) を参照してください。

## 5. `github.issue_number` のリンクと一意性（重要）

`github.issue_number` は、node（initiative/epic/issue）を GitHub Issue 番号へ紐づけるためのメタデータです。

- `new`（デフォルト）: `gh issue create` の結果（Issue番号）でリンクします
- `new --github-issue <n>`: 既存番号へリンクします（新規 Issue は作りません）
- `import <n|#n|url>`: 既存番号へリンクします（読み取り確認のみ）

制約:
- **同じ `github.issue_number` を持つ node は、ツリー全体で 1つ**である必要があります（initiative/epic/issue をまたいで一意）。
  - 重複すると `active set <n|url>` が `Ambiguous github.issue_number=...` で失敗し得ます
  - `validate` / `sync` の preflight validate でも重複は検知され、エラーになります

重複が検出された場合（復旧）:
- エラーメッセージに `type:id (meta.json path)` の競合一覧が出るので、どれか1つだけが `github.issue_number` を保持するように `meta.json` を修正してください（他は削除/変更）
- 修正後に `./spec validate` / `./spec sync` を再実行してください

## 6. よくある失敗

- `gh` が未導入/未認証で `new` が失敗する → `--no-github` を付けるか、`gh auth login` 等を先に行う
- GitHub 親スコープ配下で `new-epic` / `new-issue`（wrapper）を実行し、`gh` 不在で失敗する
  - wrapper は自動で `--no-github` へフォールバックしません
  - エラーメッセージに従い、`gh` を導入するか、意図的に direct command + `--no-github` を選んでください
- URL を貼ったのに別リポジトリの Issue が import されない → 仕様上、URL は番号抽出のみ（`owner/repo` は無視）
