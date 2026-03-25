# GitHub 連携（`gh`）の挙動

このドキュメントは、`new {initiative,epic,issue}` が **GitHub Issue を自動作成する**挙動を、コーディングエージェント向けに明確化するためのものです。

## 結論

- `new {initiative,epic,issue}` はデフォルトで **`gh issue create` を実行**します。
- spec-dock は owner/repo を自前で解決しません。
  - `gh` を導入先リポジトリの root で実行し、対象リポジトリの解決は **`gh` に委譲**します。
- GitHub を使わない場合は `--no-github` を明示し、ID は `*-local-*` 名前空間で採番します。
- `--slug` は **安全な文字のみ**許可します（空白や `!` などは禁止）
  - 許可: Unicode の英数字 + `-` `_` `.`
  - 追加制約: **小文字のみ**（大文字を含む場合はエラー）

## 1) 実行されるコマンド（概要）

### 1.1 Issue 作成（デフォルト）

```bash
gh issue create --title "<title>" --body "<body>"
```

- `--title` と `--body` を必ず渡す（非対話）
- `cwd` は導入先リポジトリ root
- `gh` の出力に含まれる URL から `/issues/<num>` を抽出し、`<num>` を ID に使用
  - 例: GitHub #123 → `iss-00123` / `epic-00123` / `init-00123`

### 1.2 既存 Issue への紐づけ（作成しない）

`--github-issue 123` を渡すと、GitHub Issue は作成せず、番号だけ紐づけます。

```bash
./spec-dock/scripts/spec-dock new issue --epic 124 --title "..." --github-issue 123
```

### 1.3 Issue ブランチ checkout（`active set <github_issue_number>`）

GitHub Issue 番号から **ブランチ作成/checkout → active 設定 → sync** まで一括で行えます。

```bash
./spec-dock/scripts/spec-dock active set 123
```

内部的に実行されるコマンド（概要）:

```bash
gh issue develop 123 --name work/iss-00123 --checkout
```

注意:
- 安全のため、**未コミット/未追跡の変更がある場合はエラーで中断**します（作業を保護するため）
- 仕様ツリー内に `github.issue_number == 123` のノードが存在しない場合もエラーになります

補足:
- `active set iss-00123` のようにノードIDで直接指定した場合でも、そのノードが GitHub Issue に紐づいていれば checkout します（initiative/epic/issue 共通）。
- ブランチ名は日本語タイトルを使わず、`work/<node-id>` 形式を使います（例: `work/iss-00123`, `work/epic-00123`, `work/init-00123`）。
- `work/<node-id>` が linked branch として既にある場合は、その既存 branch の checkout を優先します。
- linked branch に `work/<node-id>` が無い場合は、`gh issue develop --name work/<node-id> --checkout` で作成します。
- linked branch に legacy ブランチ（例: `gh-issue-123`）しか無い場合は、その legacy を一時 checkout してノードを解決し、最終的に `work/<node-id>` へ移行します（legacy が複数ある場合は非決定的なためエラー）。
- `gh issue develop --name ...` が使えない環境では、互換のため `gh issue checkout` / `gh issue develop --checkout` にフォールバックします。
- 互換フォールバックが使われた場合、最終的な branch 名は `gh` の挙動に依存するため `work/<node-id>` と一致しない可能性があります。

## 2) 「どのリポジトリに作るか」はどう決まるか

spec-dock は `--repo owner/repo` を指定しません。  
そのため、**対象リポジトリは `gh` の解釈で決まります**。

代表的な解決材料（`gh` 側）:
- カレントディレクトリが Git リポジトリであること
- `git remote` の URL（GitHub の owner/repo を含む）
- 必要に応じて `GH_REPO` 等の環境変数
- `gh auth`（認証）状態と権限

## 3) `--no-github`（ローカルのみ）

GitHub が使えない場合（GitHub リポジトリが無い、`gh` 未導入、認証不可など）は、明示的に `--no-github` を使います。

- `gh` は実行しません
- ID は衝突回避のため `*-local-*` 名前空間になります
  - `init-local-00001` / `epic-local-00001` / `iss-local-00001`

## 4) PlantUML（内部処理のイメージ）

```plantuml
@startuml
skinparam monochrome true
hide footbox

actor User
participant "runtime script\n(spec-dock/scripts/spec-dock)" as Script
participant "gh CLI" as GH
database "GitHub Issues" as GHI
participant "Local FS\n(spec-dock/initiatives/**)" as FS

User -> Script: new issue --epic <id> --title <title>
activate Script

alt default (GitHub)
  Script -> GH: gh issue create\n(cwd=repo root)
  activate GH
  GH -> GHI: Create Issue
  GHI --> GH: URL .../issues/<num>
  GH --> Script: stdout/stderr
  deactivate GH
  Script -> Script: parse <num>\n-> id=iss-<num>
else --no-github
  Script -> Script: next local id\n-> iss-local-00001
end

Script -> FS: write docs + meta.json
deactivate Script
@enduml
```

## 5) よくある失敗

- `gh` が無い: `new` がエラー → `gh` を導入するか `--no-github`
- GitHub リポジトリとして解決できない / 権限がない: `gh issue create` が失敗 → `git remote` / `gh auth` を確認
