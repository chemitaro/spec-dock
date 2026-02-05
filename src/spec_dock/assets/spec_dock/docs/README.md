# .spec-dock Docs（入口）

このディレクトリは、`spec-dock init/update` によって自動生成・更新されるドキュメントです。  
コーディングエージェント（Codex CLI）も人間も、まずはここ（`README.md`）から参照してください。

## まず知っておくべきこと（重要）

- **`new {initiative,epic,issue}` はデフォルトで GitHub Issue を自動作成します**
  - 内部的に GitHub CLI（`gh`）を実行します
  - 対象リポジトリは `gh` の解釈で決まります（spec-dock は owner/repo を推測しません）
  - `gh` が使えない / GitHub リポジトリでない場合は **エラー**になります
- GitHub を使わない場合は、必ず `--no-github` を付けてください
  - その場合、ID は衝突回避のため `*-local-*` 名前空間になります（例: `iss-local-0001`）

## クイックスタート

### 1) ノード作成（デフォルト: GitHub）

```bash
./.spec-dock/scripts/spec-dock new initiative --title "Auth platform"          # init-0123（GH #123）
./.spec-dock/scripts/spec-dock new epic --initiative 123 --title "JWT auth"    # epic-0124（GH #124）
./.spec-dock/scripts/spec-dock new issue --epic 124 --title "Add refresh token"  # iss-0125（GH #125）
```

### 2) ノード作成（ローカルのみ: `--no-github`）

```bash
./.spec-dock/scripts/spec-dock new initiative --no-github --title "Auth platform"          # init-local-0001
./.spec-dock/scripts/spec-dock new epic --no-github --initiative 1 --title "JWT auth"      # epic-local-0001
./.spec-dock/scripts/spec-dock new issue --no-github --epic 1 --title "Add refresh token"  # iss-local-0001
```

### 3) active（現在作業中）を設定

```bash
./.spec-dock/scripts/spec-dock active set --issue 125   # iss-0125 / iss-local-0001 も可
```

すると `.spec-dock/active/context-pack.md` が生成され、エージェントはそこから作業を開始できます。

## 生成物（重要）

- `.spec-dock/initiatives/`  
  仕様ツリー本体（常置。移動で状態を表現しません）
- `.spec-dock/active/`（git 管理しない）  
  現在の initiative/epic/issue への固定入口（symlink 等） + `context-pack.md`
- `.spec-dock/.work/`（git 管理しない）  
  `current.json`（SSOT）/ `state.json`（index）/ `tree.json`（tree）などの生成物

## ドキュメント構成（どれを読めばいい？）

- `spec-dock-guide.md`  
  仕様書駆動 + TDD の **ワークフロー**（要件→設計→計画→実装→レポート）
- `github.md`  
  GitHub 連携（`gh` 必須・対象リポジトリの決まり方・`--no-github`・ID ルール）
- `sync.md`  
  `sync`（状態集計）の仕組み（ローカル集計 + 任意で GitHub enrich）
