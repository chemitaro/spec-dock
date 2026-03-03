# reference: deps（依存関係管理）

対象コマンド:

```bash
./spec deps check <target> [--github] [--gh-limit N] [--json]
./spec active set <target> [--github] [--gh-limit N] [--force|-f] [--checkout]
./spec sync [--github] [--gh-limit N] [--no-update-active] [--force]
```

関連:
- 入口: [README.md](README.md)
- 総合: [guide.md](guide.md)
- sync: [reference_sync.md](reference_sync.md)

## 1. 結論（v2）

- `deps.json` の shorthand（`init-*` / `epic-*` / GitHub issue番号）を展開し、canonical な issue->issue direct edge にコンパイルします。
- `deps check` は v2 evaluator（issue-only canonical graph）で `ready / blockers / effective_depends_on` を判定します。
- `active set`（issue target）は v2の `ready` をガード条件に使い、`ready=false` ならデフォルトで失敗します。
- `sync` は `index-*.json` の `deps.issue_edges` と `deps-issues.*`（todo issue-only）を生成します。

## 2. `deps.json`（ノード直下 / 任意）

配置場所:
- initiative: `<initiative-dir>/deps.json`
- epic: `<epic-dir>/deps.json`
- issue: `<issue-dir>/deps.json`

スキーマ:

```json
{
  "schema_version": 1,
  "depends_on": [
    "iss-00123",
    "epic-local-00001",
    456,
    "789"
  ]
}
```

ルール:
- `schema_version` は `1` 固定
- `depends_on` 要素は node id または GitHub issue番号（int / 数字文字列）
- shorthand は最終的に issue->issue edge へ還元されます
- `deps.json` が無い場合は `depends_on=[]`

構造エラー（fail-fast）:
- JSONパース不正 / schema不正
- 未解決参照
- 親->配下（descendant）依存
- 自己依存（shorthand展開で生じる implicit self も含む）
- 循環依存（cycle）

補足:
- shorthand 展開結果が空でもエラーにはせず、warning `deps_ref_expanded_to_empty` を出します。

## 3. v2評価の基本

- 評価グラフは issue-only（canonical direct edges）
- `effective_depends_on` は closure かつ Done除外
- `unknown` は Done扱いしない（安全側）
- issue の `ready`:
  - `status==done` は常に `ready=true`
  - それ以外は closure が空かつ status が unknown でない場合のみ `ready=true`

## 4. `deps check`

```bash
./spec deps check <target>
./spec deps check <target> --github
./spec deps check <target> --json
```

終了コード:
- `0`: ready
- `3`: blocked（unknown を含む）
- `1`: 実行時エラー（構造エラー等）
- `2`: 引数エラー（argparse）

`--github`:
- `gh issue list` を参照して OPEN/CLOSED を判定
- 失敗時は `gh_fetch_failed` warn で unknown 扱い
- 取得漏れは `gh_index_incomplete` warn

`--github` なし:
- GitHub へアクセスしない
- snapshot は `spec-dock/.agent/index-all.json` 優先、無ければ `spec-dock/.agent/index.json`
- snapshotが無い/不足なら unknown（blocked 側）

`--json` 出力（stable keys）:

```json
{
  "schema_version": 1,
  "target": "iss-00302",
  "ready": false,
  "effective_depends_on": ["iss-00301"],
  "blockers": ["iss-00301"],
  "nodes": {
    "iss-00301": {"state": "blocked", "ready": false}
  },
  "warnings": []
}
```

## 5. `active set` の deps guard（v2）

```bash
./spec active set <issue-id>
./spec active set <issue-id> --force
```

- issue target は v2 evaluator で判定
- ブロック条件は `not ready`（`blockers` の有無ではない）
- `ready=false` かつ `--force` なし: 失敗（exit=1）し、`spec-dock/.agent/active.json` は更新しない
- `--force` あり: `deps_blocked` 警告を出して active 更新を続行
- `--github` なし時は snapshot（`index-all -> index`）を使い、無ければ unknown で blocked

## 6. `sync` における deps 生成物（v2）

`.agent/`:
- `index-all.json` / `tree-all.json`（all）
- `index.json` / `tree.json`（todo projection）
- `deps-issues.json`（todo issue-only graph）

人間向け:
- `spec-dock/deps-issues.puml`
- `spec-dock/tree-all.puml`
- `spec-dock/tree.puml`
- `spec-dock/dashboard.md`

`sync --force` かつ deps preflight失敗時:
- `deps.valid=false`, `deps.error` を持つ placeholder で上書き
- `deps-issues.json` は `nodes={}`, `edges=[]` で上書き（削除しない）

legacy v1 生成物は廃止:
- `.agent/deps.json`, `.agent/deps.puml`, `.agent/deps.todo.puml` は `sync` で削除

## 7. 矢印方向（JSON vs PlantUML）

- JSON edge（`deps.issue_edges` / `deps-issues.json.edges`）:
  - `depends_on` 方向（`dependent -> prerequisite`）
- PlantUML（`deps-issues.puml`）:
  - blocks 表示（`prerequisite -> dependent`）

同一依存を用途別に向きを変えて表現しています。
