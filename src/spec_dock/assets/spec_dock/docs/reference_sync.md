# reference: sync（状態集計）

対象コマンド:

```bash
./spec sync [--github] [--gh-limit N] [--no-update-active] [--force]
```

関連:
- 入口: [README.md](README.md)
- 総合: [guide.md](guide.md)
- deps: [reference_deps.md](reference_deps.md)

## 1. 結論（v2の生成物）

`sync` はローカル SSOT（`spec-dock/initiatives/**/.meta.json`）を走査し、v2 の観測点を生成します（git 管理しない）。
`meta.json`（レガシー名）はサポート対象外で、検出時はエラー停止します（`.meta.json` へ手動移行してください）。

`.agent/`（機械向け）:
- `spec-dock/.agent/index-all.json`（全ノード）
- `spec-dock/.agent/tree-all.json`（全ノードのツリー）
- `spec-dock/.agent/index.json`（todo projection）
- `spec-dock/.agent/tree.json`（todo projection のツリー）
- `spec-dock/.agent/deps-issues.json`（todo issue-only 依存グラフ）

`spec-dock/` 直下（人間向け）:
- `spec-dock/tree-all.puml`（Readyボード, all）
- `spec-dock/tree.puml`（Readyボード, todo）
- `spec-dock/deps-issues.puml`（todo issue-only 依存図）
- `spec-dock/dashboard.md`（todo要約）

legacy v1 生成物（廃止）:
- `spec-dock/.agent/deps.json`
- `spec-dock/.agent/deps.puml`
- `spec-dock/.agent/deps.todo.puml`

上記3つは `sync` 実行時に常に削除されます（stale防止）。

## 2. all / todo projection

`*-all.json` は全件を保持します。

`index.json` / `tree.json` は todo projection です:
- `status==done` の issue を除外
- todo issue が0件の epic / initiative を除外（empty枝除外）
- `deps.issue_edges` は端点が todo issue の edge のみ保持
- `index.json` と `tree.json` のノード集合は一致

## 3. deps情報の埋め込み

`index-*.json` / `tree-*.json` のトップレベルには `deps` が入り、少なくとも以下を持ちます:
- `valid: bool`
- `error: string | null`
- `issue_edges: [{from,to,kind?}]`
- `edge_direction: "depends_on (dependent -> prerequisite)"`

issueノードには `deps`（`ready`, `depends_on`, `blockers_top`）を統合します。

## 4. `sync --force`（deps preflight失敗時）

deps 構造エラー（未解決参照 / self / cycle / descendant依存 / schema不正など）がある場合:
- 通常 `sync`: 失敗（非0）
- `sync --force`: index/tree 更新は継続し、`deps_preflight_failed` を warn + warnings に出力

`--force` で deps 無効化時の挙動:
- `index-*.json` / `tree-*.json`: `deps.valid=false`, `deps.issue_edges=[]`, `deps.error` を設定
- issueノードの `deps` は `null`（未計算扱い）
- `spec-dock/.agent/deps-issues.json` は placeholder（`deps.valid=false`, `nodes={}`, `edges=[]`）で上書き
- `spec-dock/deps-issues.puml`, `spec-dock/tree*.puml`, `spec-dock/dashboard.md` も placeholder内容で上書き
- `--force` はデバッグ/リカバリ用途のため、depsの成否に関わらず active auto-update を無効化（`--no-update-active` 相当）

削除ではなく上書きにすることで、stale 参照を防ぎます。
`--force` 実行後に active を更新したい場合は、`./spec active set <target>` を使って明示更新してください。

## 5. `--github` とスナップショット

`sync --github`:
- `gh issue list` の読み取り結果で issue status を enrich（OPEN/CLOSED -> open/done）

`sync`（`--github` なし）:
- GitHubへアクセスしない
- 既存スナップショットを使う場合は `index-all.json` を優先し、無ければ `index.json` へ fallback
- どちらも無ければ issue status は `unknown`

## 6. active更新

デフォルトでは、ブランチ名から active を best-effort 推定して更新します。

- `sync --no-update-active`: active を更新しない
- `sync --force`: `--no-update-active` 相当として扱い、active auto-update を行わない
- `main` / `develop` など手がかりが無いブランチでは active は維持

## 7. 矢印方向（JSONとPlantUML）

- JSON（`deps.issue_edges`）: `depends_on` 方向（`dependent -> prerequisite`）
- `deps-issues.puml`: blocks 表示（`prerequisite -> dependent`）

同じ依存を、機械向けと可視化向けで向きを分けて表現しています。

## 8. PlantUML（処理フロー）

```plantuml
@startuml
skinparam monochrome true
hide footbox

actor User
participant "spec-dock\n(runtime script)" as Script
participant "Local FS\n(.meta.json)" as FS
participant "git\n(branch)" as Git
participant "gh\n(GitHub CLI)" as GH
database ".agent/index-all.json" as IndexAll
database ".agent/index.json" as IndexTodo
database ".agent/deps-issues.json" as DepsIssues

User -> Script: sync [flags]
Script -> FS: scan .meta.json
Script -> Script: preflight validate
Script -> Script: deps preflight

alt update_active (default)
  Script -> Git: current branch
  Script -> Script: infer active (best-effort)
end

alt --github
  Script -> GH: gh issue list ...
  Script -> Script: enrich statuses
else local snapshot mode
  Script -> Script: use index-all -> index snapshot
end

alt deps preflight ok
  Script -> IndexAll: write(all)
  Script -> IndexTodo: write(todo)
  Script -> DepsIssues: write(valid=true)
else deps preflight failed and --force
  Script -> IndexAll: write(deps.valid=false)
  Script -> IndexTodo: write(deps.valid=false)
  Script -> DepsIssues: write(placeholder)
end
@enduml
```
