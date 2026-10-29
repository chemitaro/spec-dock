---
種別: 設計書（Issue）
ID: "iss-00438"
タイトル: "Regenerate Dashboard From Structure Snapshot"
関連GitHub: ["#438"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00438 Regenerate Dashboard From Structure Snapshot — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- 構造のスナップショット（C10）と着手の判定の部品（I-4）だけから、今の描く関数が受け取る辞書を作り、描く関数をそのまま呼ぶ。状態の規則を作り直さない。
- 作る場所は、定期の同期の周期の手順7（I-3 の `refresh_structures`）の1か所だけにする。読むだけのコマンドの契約と約束3（ほかのコマンドは作らない）を守る。
- 構造が変わらない周期では書かない。書く失敗は、同期の結果を変えずに `state.json` に残し、`canonical status` で見える。
- C10 に `created_at` と `closed_at` を足す。版1のまま、足す前のファイルは形の検査で落として取り直す。
- 従来モードのコードと出力を変えない。

## Current / Target

- **Current**（`cee4c896b`）：`refresh_structures` は `ensure_fresh(repository, "cycle")` を行い、`dashboards_written` はいつも0。`state.json` の `dashboard` は読んだまま書き戻すだけ。`canonical status` の `dashboard` は `not_implemented`。`canonical remove` はダッシュボードに触れない。`ScopeNode` と `snapshot.json` に作成と完了の時刻はない。
- **Target**：requirement.md の R-438-01〜08。

```text
canonical sync（--registered を含む）
  手順1〜6（カタログごと、I-3）
  手順7 refresh_structures(entries, ctx, registered=…)
    for repository（最初に現れた順に1回）:
      fresh = ensure_fresh(repository, "cycle")            ← I-1、I-3（変えない）
      for その repository のカタログ:
        refresh_dashboard(entry, snapshot, store_path, …)  ← この Issue
          cycle.lock → 登録簿の確かめ → main と宣言の確かめ
          → 入力の SHA-256 と state.dashboard.input_hash を比べる
          → 書くファイルを決め、一時ファイル＋rename で書く
          → state.json の dashboard を更新（update_catalog_state）
```

## 責務・Interface

### 置き場

| 置き場 | 中身 |
|---|---|
| `domain/canonical_structure.py`（I-1） | `IssueFacts` と `ScopeNode` に `created_at: str` と `closed_at: str \| None` を足す。`_NODE_KEYS`、`_node_from_json`、`_node_json`、`_node_from_facts` に足す |
| `infra/github_structure.py`（I-1） | `FULL_READ_QUERY` の `nodes` に `createdAt closedAt` を足す。`_fetched_from_graphql` と `_facts_from_rest` で読む |
| `domain/canonical_dashboard.py`（新） | 純粋な関数：スナップショットと着手の判定から、描く関数の入力の辞書を作る。入力の SHA-256。Epic の13章は「作る部品」を `application/canonical_dashboard.py` に置くとしているが、ファイルを読み書きしない純粋な規則なので、AGENTS.md の層に従って domain に置き、application はそれを呼ぶ |
| `application/canonical_dashboard.py`（新） | 5つのファイルを描いて書く。手順7の1カタログ分（排他、確かめ、書き方、`state.json`） |
| `application/canonical_sync.py`（I-3） | `refresh_structures` に `registered` を足し、`ensure_fresh` の後に `refresh_dashboard` を呼ぶ。`run_cycle` から `registered` を渡す |
| `application/canonical_status.py`、`canonical_status_sync.py`（I-2、I-3） | `dashboard` の項目を `SyncView.dashboard_item()` で埋める |
| `application/canonical_remove.py`（I-3） | ダッシュボードの5つのふつうのファイルを消す手順を足す |
| `application/canonical_errors.py` | `CANONICAL_DASHBOARD_OCCUPIED`、`CANONICAL_DASHBOARD_FAILED` と次の1手 |
| `presentation/puml.py` | `_issue_ready_board_state` に、項目の `board_state` を使う分岐を足す（下） |
| `presentation/markdown.py` | 公開の入口 `render_dashboard_nodes_md(index_nodes)`（`_render_dashboard_md` を `active=None` で呼ぶだけ。従来の関数は変えない） |
| `infra/canonical_files.py`（I-2） | `replace_text_file(directory, name, text)`（調べたディレクトリの記述子に固定し、ランダムな名前の一時ファイルを `O_EXCL`、`O_NOFOLLOW` で作り、fsync、rename、ディレクトリの fsync。ディレクトリかシンボリックリンクがあれば `FileOccupied`）と `is_regular_file`（`lstat`）。`place_link` と同じ形 |
| `infra/canonical_registry.py`（I-3） | `is_unregistered(root, catalog)`（読める登録簿にカタログがないときだけ真）。I-3 の `sync_catalog` の同じ判定もこれを使う |
| `cli/catalog.py` | `canonical sync` と `canonical remove` のヘルプの「Writes」に、ダッシュボードを足す（`HELP_EFFECTS` の要約は変えない） |
| `tests/support/fake_github.py` | 偽の Issue に `created_at` と `closed_at` を持たせ、REST と GraphQL（問い合わせが求めたときだけ）で返す |

### C10 の追加（`snapshot.json` の版1）

- `issues` の各要素に `"created_at": "<ISO 8601 UTC>"` と `"closed_at": "<ISO 8601 UTC>" | null` を足す。`_NODE_KEYS` は鍵の集合の完全一致で調べるので、足す前のファイルは `SnapshotFormatError` になり、`SnapshotStore.load()` が None として扱い、`ensure_fresh` が取り直す（I-1 のまま）。
- GraphQL は `createdAt` と `closedAt`、REST は `created_at` と `closed_at` を読む。`closed_at` は null を許す。`created_at` は文字列で、`parse_timestamp` で読めること。
- 書き込みの反映の `UpsertIssue(facts)` は `IssueFacts` から作り直すので、そのまま入る。`SetParent` などは `replace` で今の値を保つ。

### 描く関数の入力（`domain/canonical_dashboard.py`）

```python
DASHBOARD_FILES: Final = ("dashboard.md", "tree.puml", "tree-all.puml", "deps-issues.puml", "deps-raw.puml")

@dataclass(frozen=True)
class DashboardInputs:
    index_nodes: dict[str, object]     # _render_dashboard_md の index_nodes
    tree: dict[str, object]            # _render_tree_ready_board_puml の tree_state（すべての Scope）
    deps_issues: dict[str, object]     # _render_deps_issues_puml の入力
    deps_raw: dict[str, object]        # _render_deps_raw_puml の入力

def dashboard_inputs(snapshot: StructureSnapshot) -> DashboardInputs
DASHBOARD_FORMAT: Final = 1          # 描く形を変えたら上げる（更新した SpecDock が書き直す）
def input_hash(snapshot: StructureSnapshot, *, snapshot_path: str = "") -> str
# sha256(json.dumps({"format", "snapshot_path", "issues", "external", "anomalies"}, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
```

- 対象：`snapshot.scopes`（`id` の決まった Scope）。状態は `evaluate_all(snapshot)`（I-4）の `ScopeReadiness.state`。
- 親子：`parent` の番号の先が、期待する種類（`PARENT_KINDS`）の Scope のときだけ、その子とする（従来の `children` と同じく、入れ子に入らない Scope は木に出ない）。並びは `deps_node_sort_key`。カタログのディレクトリの場所は使わない。種類のラベルを付け替えた Scope は、GitHub の今の種類と ID で示す（`SCOPE_KIND_CHANGED` は、カタログを見る `workspace validate` と `canonical status --structure` が示す。2026-10-29、Epic の `plan.md` の I-11 の節）。
- 止めているもの（`blockers_top`）：`ScopeReadiness.blockers` のうち `role` が `self` でないものの、Scope の ID を `deps_node_sort_key` の順に、続けて Scope でない Issue を番号の順に `#<番号>` で並べ、重複を除いて先頭の5件（従来の `_BLOCKERS_TOP_LIMIT`）にする。
- `index_nodes`（Issue だけ）：`{"type": "issue", "title", "status": "done" | "open", "board_state": <状態>, "deps": {"ready", "blockers_top"}}`。`_render_dashboard_md` は `status == "done"` を除くので、DONE の Issue は一覧に出ない（従来どおり）。
- `tree`：`{"tree": [initiative{id, title, epics: [epic{id, title, issues: [issue{id, title, status, board_state, deps}]}]}]}`。`tree.puml` と `tree-all.puml` は、従来どおり、同じ木を `todo_only=True` と `False` で描く。
- `deps_issues`：従来の `_build_deps_issues_v2_payload` と同じ規則。
  - ノード：DONE でないすべての Issue と、辺の両端。Issue は `{"type": "issue", "state": <小文字の状態>, "ready"}`。Epic と Initiative は `{"type", "state": "open" | "closed", "ready": state == "closed"}`（従来の高い階層の見え方。`ready` が偽なら描く関数が `ready=false` を付ける）。
  - 辺：DONE でない Issue から、`blockers` の `role == "prerequisite"` の Scope へ、`state: "blocking"`（従来の `raw_direct` の辺に当たる）。従来の Issue に広げた辺（`compiled_issue`）は、canonical の着手の判定が前提の Epic と Initiative を配下に広げないので作らない。祖先と Scope でない Issue への辺も作らない（従来の辺は Scope のノードの間だけ）。描く関数は `from`、`to`、`state` だけを読むので、`relation` と `source` は持たせない。
- `deps_raw`：従来の `_build_deps_raw_payload` と同じ規則。
  - 参加者：宣言した依存（`blocked_by` の Scope）の両端がどちらも「進行中」で、前提が `completed` でない辺。進行中は、Issue なら開いている、Epic と Initiative なら、開いていて、配下の Issue があるならそのどれかが開いている。
  - 参加者の祖先を足した木を描く。Issue は `state`（小文字の状態）、Epic と Initiative は `state`（`open` か `closed`）と `state_source: "github"`。
- 題名は、すべて GitHub の題名をそのまま入れる（逃がしは描く関数が行う）。

### 描く関数の変更（`presentation/puml.py`）

```python
def _issue_ready_board_state(issue_id, issue_item, *, active_issue_id):
    ...（status、ready、blockers_top を今のまま求める）
    board_state = issue_item.get("board_state")
    if board_state in ("READY", "BLOCKED", "DOING", "DONE", "UNKNOWN"):
        return (board_state, blockers_top if board_state in ("BLOCKED", "DOING", "UNKNOWN") else [])
    ...（今のまま）
```

- 従来の入力は `board_state` を持たないので、出力は変わらない（AC-438-09。変更の前の関数の出力と比べるテスト）。戻す `blockers_top` は、今の分岐と同じく、DONE と READY では空にする。
- `_render_dashboard_md` と `_render_tree_ready_board_puml` は、この関数を通るだけで、変えない。

### 書く部品（`application/canonical_dashboard.py`）

```python
@dataclass(frozen=True)
class DashboardOutcome:
    written: tuple[str, ...]     # 書いたファイル名
    error: Mapping[str, object] | None
    skipped: str | None          # "cycle_busy"、"unregistered"、"not_main"、"legacy_mode"（state を変えない）

def render_dashboard_files(snapshot: StructureSnapshot, *, snapshot_path: Path) -> dict[str, str]
def refresh_dashboard(entry: RegistryEntry, snapshot: StructureSnapshot | None, *, snapshot_path: Path,
                      state_root: Path, now: str, registered: bool) -> DashboardOutcome
```

- `render_dashboard_files`：`dashboard_inputs` を描く関数に渡し、`dashboard.md` の「Observability」の最初の行を `- snapshot: \`<snapshot_path>\`` に置き換える。どのファイルも末尾を改行1つにそろえる（従来の `render_dashboard` と同じ）。
- `refresh_dashboard` の順：
  1. `cycle_lock(state_root, catalog)`（待たない）。取れなければ `skipped="cycle_busy"`。
  2. `registered` なら登録簿を読み直し、カタログがなければ `skipped="unregistered"`。
  3. `main_checkout/.git` がディレクトリでなければ `skipped="not_main"`。`main/spec-dock` が（リンクでない）ディレクトリで、`probe_workspace_mode(main)` が `canonical` でなければ `skipped="legacy_mode"`。`spec-dock/` がない、ディレクトリでない、リンクのときは、宣言を読めないので従来モードとは見なさず、手順5で `CANONICAL_DASHBOARD_FAILED` を記録する（R-438-04。最終品質ゲート1の SP の P2）。
  4. `read_catalog_state` が None なら `skipped="no_state"`（手順1〜6が基準とともに作る記録を、ここで基準なしに作らない）。`dashboard.input_hash` と `input_hash(snapshot, snapshot_path=…)` を比べ、書くファイルを決める（違えば5つ、同じならふつうのファイルとしてないものだけ）。スナップショットがなければ書かずに `CANONICAL_DASHBOARD_FAILED`。
  5. `main/spec-dock` を `lstat` し、ディレクトリ（リンクでない）でなければ `CANONICAL_DASHBOARD_FAILED`。ファイルごとに、`lstat` でディレクトリかシンボリックリンクなら飛ばして `CANONICAL_DASHBOARD_OCCUPIED` の `paths` に足す。ほかは `replace_text_file` で、ディレクトリの記述子に固定したうえで、ランダムな名前の一時ファイル `.<名前>.<16桁の16進>.tmp` を `O_EXCL | O_NOFOLLOW` で作り、fsync してから rename し、ディレクトリも fsync する（失敗すれば一時ファイルを消し、`CANONICAL_DASHBOARD_FAILED`）。
  6. `update_catalog_state` で `dashboard = {"input_hash": <今の SHA-256>, "written_at": <書いたら now、でなければ前の値>, "error": <あれば>}` を書く（今の記録の `dashboard` だけを置き換える）。スナップショットがないときと、`CANONICAL_DASHBOARD_FAILED` のときの `input_hash` は前の値のまま（次の周期で5つを書き直す）。
- 例外：カタログごとの呼び出しの例外は、種類を問わず `refresh_structures` の中で受け止めて同期のログに残し、そのカタログの `dashboards_written` に数えない。同期の結果は変えない。`state.json` が読んだ後に消えたときは、作り直さずに `skipped="no_state"` にする。

### `refresh_structures` の変更

```python
def refresh_structures(entries, ctx, *, registered: bool = False) -> list[RepositoryResult]
```

- `ensure_fresh` の結果（例外のときは None）の `snapshot` で、その `repository` の各エントリー（`entries` の順）に `refresh_dashboard` を呼ぶ。`snapshot_path` は `SnapshotStore(ctx.state_root, repository).directory / "snapshot.json"`。
- `dashboards_written` は、`written` が空でないカタログの数。`repository` が null のカタログは、今と同じく対象外。

### `canonical status` の `dashboard`

```json
{"status": "ok | missing | problem", "next_step": null, "directory": "<main>/spec-dock",
 "files": {"dashboard.md": true, "tree.puml": true, ...}, "written_at": "...", "error": null}
```

- `error` があれば `problem` にし、そのコードで `warnings` に入れる（`details.item = "dashboard"`、`details.next_step`、`details.paths`）。そろっていて `error` がなければ `ok`、ほかは `missing`（次の1手は `DASHBOARD_MISSING_NEXT_STEP`。警告にしない）。リポジトリが分からないクローンは `not_applicable`。`state.json` が読めないときは `error` と `written_at` を null にする（読めないことは `sync` の項目が警告する）。`missing` と `not_applicable` は、この項目の新しい値である。

### `canonical remove`

- 手順の一覧の、カタログのworktreeを外した後、`info/exclude` の前に、`main/spec-dock/<名前>` が `lstat` でふつうのファイルのものごとに `_Step("canonical.dashboard.remove", <パス>, unlink, (main/spec-dock,))` を足す。

### エラーのコード（C8。Epic の12章への追記は統括）

| コード | 記録する場所 | 次の1手 |
|---|---|---|
| `CANONICAL_DASHBOARD_OCCUPIED` | `state.json` の `dashboard.error`、`canonical status` の警告 | Move the listed paths away; the next sync writes the dashboard there. |
| `CANONICAL_DASHBOARD_FAILED` | 同上 | Check the snapshot and sync items of spec-dock canonical status. |

## data / failure

- 書くもの：mainのチェックアウトの `spec-dock/` の5つのファイル（Git で無視される）、`state.json` の `dashboard`。読むもの：構造のスナップショット、登録簿、`state.json`、mainのチェックアウトの宣言。
- 失敗は requirement.md の「失敗・境界条件」の表のとおり。どの失敗も、手順1〜6の結果、`canonical sync` の結果の状態、終了コードを変えない。
- 5つのファイルは、1つずつ `rename` で置き換えるので、どの時点でも各ファイルは完全である（5つの間の一致は保証しない。次の周期で欠けたものを書く）。

## 変更対象

- 変える：上の「置き場」の表のもの。I-3 のテストのうち、`dashboards_written` が0であることを前提にしたもの（`tests/cli_runtime/test_issue430_canonical_sync.py` の2つ）と、`dashboard` が `not_implemented` であることを確かめるもの（あれば）を、canonical のテストとして直す。
- 変えない：従来モードの処理、`.meta.json` の読み書き、`presentation/json_state.py`、`presentation/markdown.py` の従来の関数（公開の入口を1つ足すだけ）、版3のテスト、I-4 の着手の判定の規則、`snapshot.json` の版、配布資産。

## 移行・互換性・rollback

- 0.3.0 の前で、利用者の状態の置き場にはまだスナップショットがない。足す前の形のファイルがあっても、取り直すだけである。
- 戻すときは PR を `git revert` する。戻した後に、足した項目のある `snapshot.json` は、I-1 の形の検査で落ちて取り直される。ダッシュボードのファイルは Git で無視されるので、残っても害はない。

## testability

- **単体**：`tests/unit/domain/test_canonical_dashboard.py`（`dashboard_inputs` の状態、親子、ブロッカー、deps-issues と deps-raw の規則、`input_hash`）。`tests/unit/presentation/test_dashboard_board_state.py`（`board_state` の分岐と、従来の入力で出力が変わらないこと）。`tests/unit/domain/test_canonical_structure.py` と `tests/unit/infra/test_github_structure.py`、`test_github_snapshot.py`（時刻の項目、要求の数、古い形の取り直し）。
- **見本との比較**：`tests/unit/application/test_canonical_dashboard_golden.py`。見本の `tree-all.puml` と `dashboard.md` から Scope の ID、題名、状態を読み、偽の `gh` に同じ構造を作り、全体の取り直しのスナップショットから描いた5つを、見本と比べる（ローカルの ID の置き換えと、Observability の行のほかは一致）。
- **周期**：`tests/cli_runtime/test_issue438_canonical_dashboard.py`。I-3 の `SyncPair` と偽の `gh` で、作成、書かない周期、題名の変更、欠けたファイル、ディレクトリとシンボリックリンク、作業用のworktree、版3の main、main の `spec-dock/` がない・ファイル・リンク、スナップショットなし、`canonical status`、`canonical remove`。
- **従来モード**：`tests/unit/presentation/` の今のテストと、版3のテストを変えずに通す。

## risk

| リスク | 影響 | 対策 |
|---|---|---|
| I-5 と `ScopeNode`、`IssueFacts`、`apply_changes` で衝突する | 中 | 項目を足すだけにする。先に入った方を `origin/main` のマージで取り込む |
| 描く関数の変更で、従来の出力が変わる | 中 | `board_state` がないときは今の分岐を通る。変更の前の関数の写しと出力を比べるテスト |
| 手順7と `canonical remove` の競合で、消したファイルや `state.json` を作り直す | 低 | `cycle.lock` と、`--registered` の登録簿の読み直し |
| 見本の構造（ローカルの ID）が canonical で作れない | 低 | 並びの変わらない番号に置き換えて比べる |
| 見本に BLOCKED、DOING、依存の辺がなく、見本の比較で確かめられない | 中 | 単体のテストで、状態、`blockers:`、辺、参加者を、従来の規則から書いた期待値で確かめる |
