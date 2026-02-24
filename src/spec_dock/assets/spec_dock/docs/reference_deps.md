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

## 1. 結論（何ができるか）

- ノード（initiative/epic/issue）ごとに `deps.json` で依存関係を定義できます（SSOT は `meta.json` とは別）。
- `deps check` で「着手可能（ready）か / 何がブロッカーか」を機械判定できます。
- `active set` は依存未解決をデフォルトでブロックし、`-f/--force` でのみ例外化できます。
- `sync` は依存関係を統合して `.agent/deps.json` と PlantUML（全体/Done除外）を生成します。

## 2. `deps.json`（ノード直下 / 任意）

配置場所:
- initiative: `<initiative-dir>/deps.json`
- epic: `<epic-dir>/deps.json`
- issue: `<issue-dir>/deps.json`

スキーマ（MVP）:

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
- `schema_version` は `1` 固定（それ以外はエラー）。
- `depends_on` の要素は次を許可します:
  - node id 文字列（`init-*` / `epic-*` / `iss-*`）
  - GitHub issue number（`int` または数字文字列）
- 親→配下（descendant）依存は禁止:
  - 例: initiative が配下 epic/issue を depends_on に含める、epic が配下 issue を depends_on に含める
  - 理由: issue/epic は親依存を継承するため、親→子依存は子の自己依存/循環に発展する
- 依存参照は解決後に node id へ正規化し、重複は排除されます。
- `deps.json` が無い場合は `depends_on=[]`（依存なし）として扱います。

エラーになる代表例:
- JSON パース不正 / スキーマ不正
- 解決不能参照（存在しない id / 未 import の GitHub issue number）
- 親→配下（descendant）依存
- 自己依存 / 循環依存（cycle）

## 3. 実効依存（親の依存をマージ）

- initiative: 自身の依存のみ
- epic: 自身 + 親 initiative
- issue: 自身 + 親 epic + 親 initiative

## 4. 状態（state）と ready 判定

状態（MVP）:
- `done`: GitHub `CLOSED`
- `doing`: active leaf（`issue` > `epic` > `initiative`）
- `todo`: GitHub `OPEN`（ただし doing ではない）
- `unknown`: `--github` 無し / `github.issue_number` 無し / `gh` 取得失敗 / `gh` 取得漏れ
- `blocked`: 依存未解決（ready=false）の導出状態

ready:
- `ready = effective_depends_on がすべて done`
- `unknown` は未解決として扱われるため、通常 blocked になります（安全側）
  - 補足: `state` と `ready` は別軸です（`state=done` でも `ready=false` は起こり得ます）。

## 5. `deps check`（ready / blockers）

```bash
./spec deps check <target>
./spec deps check <target> --github
./spec deps check <target> --github --json
```

終了コード:
- `0`: ready（実行可能）
- `3`: blocked（依存未解決 / unknown を含む）
- `1`: 構造エラー（deps.json 不正、解決不能参照、cycle など）
- `2`: 引数エラー（argparse）

`--github`:
- `gh issue list` を使って OPEN/CLOSED を取得し、Done 判定に使います。
- 取得できない場合は `gh_fetch_failed` として warn し、unknown 扱いで継続します。
- 一部の linked issue が取得できていない場合は `gh_index_incomplete` として warn します（`--gh-limit` 調整のヒント）。

## 6. `active set`（依存ガード / force）

```bash
./spec active set <target> --github
./spec active set <target> --github --force
./spec active set <target> --github -f
```

- blocked の場合、デフォルトでは失敗し active は更新されません。
- `-f/--force` の場合、警告を出した上で active 化します（順番違反の可視化のため）。

## 7. `sync` の deps 派生物（.agent）

`sync` は依存関係も統合し、以下を生成します（git 管理しない）:

- `spec-dock/.agent/deps.json`（依存グラフの統合 SSOT）
- `spec-dock/.agent/deps.puml`（全体: Done を含む）
- `spec-dock/.agent/deps.todo.puml`（todo-only: Done を除外）

PlantUML の色（state）:
- done: `#D5E8D4`
- doing: `#DAE8FC`
- todo: `#FFF2CC`
- unknown: `#EEEEEE`
- blocked: `#F8CECC`

`sync --force` と deps 構造エラー:
- deps 構造エラー（循環依存/未解決参照など）がある場合、通常 `sync` は失敗します。
- `sync --force` の場合は warn code `deps_preflight_failed` を出して index/tree の更新を継続しますが、deps 派生物（`.agent/deps*.{json,puml}`）は削除されます（古い派生物の誤用を防ぐため）。
