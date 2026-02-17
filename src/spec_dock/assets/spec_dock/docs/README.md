# spec-dock docs（入口）

このディレクトリは `spec-dock init/update` により導入先リポジトリへ配置されます。  
人間もコーディングエージェントも、まずはここから参照してください。

## エージェント起点（Codex CLI）

Codex CLI を使う場合、このリポジトリは `.agents/skills/spec-driven-tdd-workflow/SKILL.md` を起点に運用できます。  
`spec-dock init/update` はこの skill をデフォルトで導入します。

## まず読む（全員）

1. [guide.md](guide.md)（全体像・概念・生成物・ディレクトリ構成）
2. 実施する作業のワークフロー
   - [workflow_initiative.md](workflow_initiative.md)
   - [workflow_epic.md](workflow_epic.md)
   - [workflow_issue.md](workflow_issue.md)
   - [workflow_adr.md](workflow_adr.md)
3. 仕組みを確認したい場合（参照）
   - [reference_github.md](reference_github.md)
   - [reference_naming.md](reference_naming.md)
   - [reference_sync.md](reference_sync.md)

## 目的別ショートカット

| やりたいこと | 参照 |
|---|---|
| まず概念を把握したい | [guide.md](guide.md) |
| Initiative を作る/運用する | [workflow_initiative.md](workflow_initiative.md) |
| Epic を作る/運用する | [workflow_epic.md](workflow_epic.md) |
| Issue を実装する（TDD） | [workflow_issue.md](workflow_issue.md) |
| 議論/意思決定を ADR に切り出す | [workflow_adr.md](workflow_adr.md) |
| GitHub 連携の前提/副作用を知りたい | [reference_github.md](reference_github.md) |
| `--title`/`--slug`/ブランチ命名のルールを知りたい | [reference_naming.md](reference_naming.md) |
| `sync` の入出力/フラグを知りたい | [reference_sync.md](reference_sync.md) |

## コマンド早見（最短）

```bash
./spec new initiative --title "..."              # デフォルト: GitHub Issue を作る
./spec new epic --initiative <id> --title "..."
./spec new issue --epic <id> --title "..."

./spec import issue <num-or-url> --title "..." --epic <id>  # 既存 GitHub Issue を取り込む（読み取りのみ）

./spec active set <id|#num|url>               # 作業対象をアクティブ化（デフォルト: no-checkout）
./spec active set <id|#num|url> --checkout   # アクティブ化 + ブランチ作成/切替
./spec active show

./spec validate
./spec sync
```

補足:
- `./spec` は `spec-dock init/update` が repo root に best-effort で作成するショートカット（symlink）です。無い場合は `./spec-dock/scripts/spec-dock ...` を使ってください。

## スコープ内ショートカット（生成後ノード）

ノード生成後は、各スコープ配下に wrapper が配置されます（引数はタイトル1つのみ）。

```bash
# initiative配下で epic を追加
<initiative-dir>/epics/new-epic "..."

# epic配下で issue を追加
<epic-dir>/issues/new-issue "..."

# initiative / epic / issue 配下の adrs で ADR を追加
<scope-dir>/adrs/new-adr "..."
```

補足:
- 補足資料は `artifacts/` に置き、初期ファイルとして `artifacts/_template.md` が入ります。
- 新規ノードにはテンプレ由来の `README.md` は生成されません。

## 重要な注意（事故防止）

- `new {initiative,epic,issue}` はデフォルトで `gh` を呼び、GitHub Issue を自動作成します（GitHub を使わない場合は `--no-github` を付けてください）。
- `new/import {initiative,epic,issue}` の `--title`/`--slug` には入力制約があります（ASCII / kebab-case）。詳細は [reference_naming.md](reference_naming.md) を参照してください。
- `import` は GitHub を更新しません（`gh issue view` による **存在確認のみ**）。ただしローカルにはノードを生成し、`sync --no-update-active` 相当まで実行します。
- `import` の URL 入力は **番号抽出のみ**です（`owner/repo` は無視され、別リポジトリ URL を貼っても「現在の `gh` が見ているリポジトリの同番号」として解釈され得ます）。
