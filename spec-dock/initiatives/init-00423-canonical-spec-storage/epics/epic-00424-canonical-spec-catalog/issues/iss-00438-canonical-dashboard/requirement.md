---
種別: 要件定義書（Issue）
ID: "iss-00438"
タイトル: "Regenerate Dashboard From Structure Snapshot"
関連GitHub: ["#438"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00438 Regenerate Dashboard From Structure Snapshot — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

表示名：canonical モードで、定期の同期が、構造のスナップショットから今までの形のダッシュボードを作り直す（Epic の I-11）

## 目的

今までと同じ Markdown と PlantUML のダッシュボードが、日本語の題名と、どのPCで作業中かを含めて、いつも新しい状態で mainのチェックアウトにある。次の Epic の HTML のダッシュボードまでのつなぎになる。

- 材料：Epic の `plan.md` の「I-11 Regenerate Dashboard From Structure Snapshot」の節（価値、作るもの、受け入れ、注意）と、Epic の `design.md` の担当の章（13章、2章の C10 の `created_at` と `closed_at`、3章の `canonical status` の `dashboard` と `canonical remove`、5章の `state.json` の `dashboard` と周期の手順7、12章の `canonical sync` の JSON）。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存：I-3（`iss-00430`）、I-4（`iss-00431`）。Planning Level：standard（理由は `plan.md`）。
- この Issue は、C9（I-3）と C10（I-1）と、着手の判定の部品（I-4 の `domain/canonical_readiness.py`）を、変えずに使う。C10 の `issues` の各要素に `created_at` と `closed_at` を足すのは、Epic の `plan.md` の I-11 の節と `design.md` 2章が、この Issue に割り当てたものである（版は1のまま）。
- Epic の文書で決まっていなかった点は、統括の判断（2026-10-26。`plan.md` の「統括の判断」）を正本とする。

## 背景

- 今の CLI には、`spec-dock/dashboard.md` と4つの PlantUML のファイルを作るコマンドがない（2026-10-01 のコミット `ae6c94369` で、書く部品が消えた）。描く関数（`presentation/markdown.py` の `_render_dashboard_md`、`presentation/puml.py` の `_render_tree_ready_board_puml`、`_render_deps_issues_puml`、`_render_deps_raw_puml`）は残っているが、どこからも呼ばれていない。
- 利用者は、spec-dock のmainのチェックアウトの5つのファイル（2026-09-21 に作られたもの）で、着手できる Issue と全体の進み具合を見てきた。canonical モードへの切り替え（I-10）の後は、これを構造のスナップショットから作り直す必要がある。
- I-3 が、定期の同期の周期の手順7（`ensure_fresh(repository, "cycle")`）と、`state.json` の `dashboard` の置き場と、`canonical sync --json` の `dashboards_written` の項目を置いた。I-4 が、スナップショットからの着手の判定の部品を置いた。
- HTML のダッシュボード（epic-00427）は、時間の軸（進み具合の推移、最近の動き）のために、各 Issue の作成と完了の時刻を構造のスナップショットから読む（Epic の R-I6）。
- 関係者：
  - 利用者：mainのチェックアウトを開けば、どのPCで作業中のものも含めて、今の状態が日本語の題名で見えること。
  - epic-00427 の担当：スナップショットの `created_at` と `closed_at` を、版1の形のまま読めること。
  - 移行していないリポジトリ（版3）：今と同じに動くこと（AC-15）。

## 観測可能な要件

### R-438-01 スナップショットの作成と完了の時刻

- 構造のスナップショット（`snapshot.json`、版1）の `issues` の各要素は、`created_at`（GitHub の `createdAt`）と `closed_at`（GitHub の `closedAt`。閉じていなければ null）を持つ。全体の取り直し（GraphQL）、Issue の読み直し（REST の `created_at`、`closed_at`）、書き込みの反映のどれでも入る。
- 全体の取り直しの GitHub への要求の数は、今と変わらない（問い合わせに項目を足すだけ）。
- 読む側は、この2つの項目のない版1のファイルを、壊れたファイルと同じく使わず、取り直す。版の番号は1のままにする。

### R-438-02 ダッシュボードの5つのファイル

- canonical モードの定期の同期（`canonical sync`、`--registered` を含む）は、周期の手順7で、構造のスナップショットから、mainのチェックアウトの `spec-dock/` に次の5つを作る：`dashboard.md`、`tree.puml`、`tree-all.puml`、`deps-issues.puml`、`deps-raw.puml`。
- 形は、今までと同じにする。見本は、2026-09-21 に作られた5つのファイル（この Issue で `tests/fixtures/issue438/legacy-dashboard/` に写した）である。違いは次の3つだけとする。
  - 題名は、スナップショットの GitHub の題名（日本語を含む）を使う。PlantUML の文字列には、今の描く関数の扱い（`\` と `"` の逃がし）で入れる。
  - 作業中（DOING）は、GitHub の作業中のラベル（`spec-dock:in-progress`）で決める。どのPCで作業中のものも、いくつでも示す。
  - `dashboard.md` の「Observability」の最初の行は、`.agent/index.json` の代わりに、構造のスナップショットの絶対パス（`- snapshot: \`<状態の置き場>/github/<host>/<owner>/<repo>/snapshot.json\``）を示す。
- 状態の決め方は、I-4 の着手の判定の部品の結果をそのまま使う。DONE は閉じた Issue（理由を問わない）、UNKNOWN は対象か祖先か前提に異常があるもの、DOING は開いていて作業中のラベルがあるもの、BLOCKED は、対象か祖先が宣言した前提の Scope が完了（`completed`）で閉じていないもの（`not_planned` で閉じた前提も止める）、開いた Scope でない同じリポジトリの Issue への依存があるもの、閉じた祖先があるもの、READY はそれ以外である（優先は DONE > UNKNOWN > DOING > BLOCKED > READY）。
- 止めているものの表示（`dashboard.md` の `blockers:`、`tree.puml` の `blockers:`）は、Scope を ID の順に、続けて Scope でない Issue を `#<番号>` の順に並べ、従来と同じく先頭の5件にする。
- `deps-issues.puml` の辺は、開いた Issue から、それを止めている前提の Scope へ引く。canonical の着手の判定は前提の Epic や Initiative を配下の Issue に広げないので、従来の Issue に広げた辺（`compiled_issue`）は作らない。`deps-raw.puml` は、従来と同じく、どちらの端も進行中で、前提が完了していない宣言された依存と、その祖先を描く。

### R-438-03 作り直す時

- カタログごとに、スナップショットの `issues` と `external` の中身の SHA-256 が、そのカタログの `state.json` の `dashboard.input_hash` と違うときは、5つすべてを書き直す。SHA-256 には、異常の一覧（別のリポジトリの依存が足されると、`issues` が変わらずに状態が UNKNOWN に変わるため）、描く形の版、構造のスナップショットのパス（Observability の行）も入れる（Epic の13章の「`issues` と `external`」を、表示の変化を落とさないように広げたもの）。同じときは、5つのうち、ふつうのファイルとしてないものだけを書く。どれも当たらなければ書かない（更新の時刻が変わらない）。
- GitHub につながらず、スナップショットが前のままのときも、上の規則で決める（欠けたファイルは前のスナップショットから書く）。
- ほかのコマンド（`workspace sync` を含む）は作らない。

### R-438-04 書き方と書かない場合

- ファイルごとに、同じディレクトリの一時ファイルに書いてから `rename` する。
- 書く場所にディレクトリかシンボリックリンクがあるときは、そのファイルを書かず、ほかのファイルは書く。`state.json` の `dashboard.error` に `CANONICAL_DASHBOARD_OCCUPIED` を記録する。
- スナップショットがない、mainのチェックアウトの `spec-dock/` がディレクトリでない、書き込みに失敗した、のどれかのときは、`dashboard.error` に `CANONICAL_DASHBOARD_FAILED` を記録する。
- 作業用のworktreeには書かない。登録簿の `main_checkout` の `.git` がディレクトリでないとき（作業用のworktree）と、そのチェックアウトの宣言が canonical モードでないとき（従来モード）は、書かず、`state.json` も変えない。
- 定期の同期の結果（手順1〜6、`canonical sync` の結果の状態と終了コード）は、ダッシュボードの成否で変わらない。
- そのカタログの `state.json` がまだないとき（手順1〜6が一度も記録していない）は、書かず、`state.json` も作らない（基準のない記録を作らないため）。
- `CANONICAL_DASHBOARD_FAILED` で終わったときは、`input_hash` を前の値のまま残し、次の周期で5つを書き直す（古い中身のファイルを残さないため）。

### R-438-05 記録と結果

- `state.json` の `dashboard` は `{"input_hash": "<sha256>", "written_at": "<最後に1つ以上書いた時刻>", "error": null | {"code", "message", "at", "paths"}}` である。失敗のない回で `error` を null に戻す。
- `canonical sync --json` の `data.repositories[].dashboards_written` は、そのリポジトリで1つ以上のファイルを書いたカタログの数である。

### R-438-06 `canonical status` の `dashboard` の項目

- `dashboard` の項目は、`status`、`next_step`、`directory`（mainのチェックアウトの `spec-dock/`）、`files`（5つのファイルの名前ごとに、ふつうのファイルとしてあるか）、`written_at`、`error` を示す。
- `dashboard.error` があれば `status` を `problem` にし、そのコードと次の1手を `warnings` に入れる（終了コードは0のまま）。5つのファイルがそろい、`error` がなければ `ok`、それ以外（まだ作っていない）は `missing`（次の1手は「次の定期の同期が作る。`canonical status` の `sync` を確かめる」。警告にはしない）にする。このクローンの GitHub のリポジトリが分からないとき（ダッシュボードを作らない）は `not_applicable` にする。`state.json` が読めないときは、`sync` の項目の警告（I-3）に任せ、`error` と `written_at` を null にして、ファイルの有無で決める。
- 何も書かず、GitHub に問い合わせない。

### R-438-07 `canonical remove`

- `canonical remove --yes` は、mainのチェックアウトの5つのダッシュボードのファイルのうち、ふつうのファイルを消す。ディレクトリとシンボリックリンクは消さない。`--yes` がないときは、予定（`planned`）に含めるだけで消さない。

### R-438-08 描く関数の出力の形

- 描く関数を直すときも、従来の入力に対する出力は、1文字も変えない。

## スコープ

- 対象：R-438-01〜08 の実装とテスト、見本の写し（`tests/fixtures/issue438/legacy-dashboard/`）、`canonical sync` と `canonical remove` のヘルプの「Writes」の文。
- 対象外：
  - HTML のダッシュボードと、Epic と Initiative の状態の配下からの集計（epic-00427）。
  - 使い方の文書（`spec-dock/docs/canonical.md` のダッシュボードの節）と、Epic の12章のエラーのコードの表への追記（I-9 と統括）。
  - 配布資産の変更（5つのファイルは配布資産の `spec-dock/.gitignore` で、すでに無視されている）。
- 親契約として維持する境界：
  - C9 と C10 の公開の形は、`created_at`、`closed_at`、`dashboard` の項目を足すほかは変えない。`snapshot.json` の版は1のまま。
  - 着手の判定の部品（I-4）の規則と公開の形を変えない。
  - 従来モードの処理、`.meta.json` の読み書きのコード、版3の振る舞いのテストを変えない（AC-15）。

## 失敗・境界条件

| 場面 | 振る舞い |
|---|---|
| GitHub につながらない、スナップショットあり | 前のスナップショットで、R-438-03 の規則（欠けたファイルだけを書く） |
| GitHub につながらない、スナップショットなし | 書かない。`dashboard.error` に `CANONICAL_DASHBOARD_FAILED` |
| 書く場所にディレクトリかシンボリックリンク | そのファイルだけ書かない。`CANONICAL_DASHBOARD_OCCUPIED`（`paths` にパス） |
| mainのチェックアウトの `spec-dock/` がない、書けない | 書かない。`CANONICAL_DASHBOARD_FAILED` |
| 登録簿の `main_checkout` が作業用のworktree、または宣言が版3 | 書かない。`state.json` も変えない |
| カタログの周期の排他（`cycle.lock`）が取れない | そのカタログは今回は飛ばす（次の周期で書く） |
| `--registered` の周期の途中で `canonical remove` が登録簿から外した | そのカタログは飛ばす（消したファイルと `state.json` を作り直さない） |
| 手順7の前に終わりの合図（SIGTERM） | 手順7ごと行わない（I-3 のまま） |
| カタログが一時停止している、手順1〜6で飛ばされた | 手順7は行う（Epic の手順7） |
| そのカタログの `state.json` がない | 書かない。`state.json` も作らない |
| `state.json` が読めない | そのカタログは書かずに、同期のログに残す（同期の結果は変えない） |
| 異常のある Scope、別のリポジトリの関係、スナップショットにない依存先 | UNKNOWN |
| 2つの項目のない版1の `snapshot.json` | 使わずに取り直す |

## 受け入れ条件

テストは、外のネットワークを使わない（偽の `gh`、一時ディレクトリの bare のリポジトリ、`XDG_STATE_HOME` と `--state-root` を一時ディレクトリに）。I-3 の `tests/conftest.py` の2段の防ぎの中で書く。

- **AC-438-01**（R-438-01）：偽の `gh` の上で、全体の取り直しのスナップショットに、開いた Issue の `created_at`（`closed_at` は null）と、閉じた Issue の `created_at` と `closed_at` が入る。取り直しの要求が、項目を足す前と同じく、変わったかの確かめの3回と GraphQL の1回の、合わせて4回である（偽の `gh` の記録で確かめる）。GraphQL の問い合わせが `createdAt` と `closedAt` を求める。読み直し（`reread`）と書き込みの反映（`UpsertIssue`）でも入る。2つの項目のない版1の `snapshot.json` を置いた状態の `ensure_fresh` が、それを使わずに取り直す。
- **AC-438-02**（R-438-02）：一時のカタログと偽の `gh` で、`canonical sync` の後に、mainのチェックアウトの `spec-dock/` に5つのファイルができる。見本と同じ形のスナップショットから作った5つのファイルが、見本と、題名、作業中の決め方、Observability の行のほかは1行ずつ一致する（見本の中の Scope と同じ ID と題名と状態を、偽の `gh` に作って比べる。見本のローカルの ID `init-local-00002` と `init-local-00003` は canonical モードでは作れないので、並びの変わらない番号の ID に置き換えて比べる）。日本語の題名と `"` を含む題名が、PlantUML の文字列として正しく入る。
- **AC-438-03**（R-438-02。`tests/unit/domain/test_canonical_dashboard.py` のスナップショットだけを入力にした単体のテストと、周期のテスト）：作業中のラベルのある開いた Issue が DOING（2つ以上でも）、閉じた Issue が DONE、開いた前提の Scope のある Issue が BLOCKED、開いた Scope でない Issue への依存のある Issue が BLOCKED、異常のある Issue が UNKNOWN、それ以外が READY として、`dashboard.md` の一覧と、`tree.puml`、`tree-all.puml`、`deps-issues.puml` の色と状態に出る。`blockers:` の並びと5件の上限、`deps-issues.puml` の辺（開いた Issue から前提の Scope へ。前提が Epic でも辺を引く）、`deps-raw.puml` の参加者（完了した前提と、配下の Issue がすべて閉じた Epic は入らない）と祖先が、R-438-02 のとおりである。異常だけが変わったときも書き直す。
- **AC-438-04**（R-438-03、AC-17）：構造が変わらない次の周期では、5つのファイルを書かない（更新の時刻と中身が変わらない）。`dashboards_written` が0になる。GitHub で題名を変えた後の周期では書き直し、新しい題名が出る。1つのファイルを消した後の周期では、そのファイルだけを書く。
- **AC-438-05**（R-438-04）：書く場所にディレクトリかシンボリックリンクがあると、そのファイルを書かず（シンボリックリンクの先も変わらない）、ほかの4つは書き、`state.json` の `dashboard.error` が `CANONICAL_DASHBOARD_OCCUPIED` でそのパスを持つ。同期の結果は `succeeded` か `unchanged` のままである。取り除いた後の周期で、そのファイルが書かれ、`error` が null に戻る。
- **AC-438-06**（R-438-04）：作業用のworktreeで `canonical sync` をしても、ダッシュボードは mainのチェックアウトにだけでき、作業用のworktreeの `spec-dock/` には作られない。登録簿の `main_checkout` が作業用のworktreeを指すときと、mainのチェックアウトの宣言が版3のときは、書かず、`state.json` の `dashboard` も変わらない。スナップショットがなく GitHub にもつながらないとき、書かずに `CANONICAL_DASHBOARD_FAILED` を記録する。
- **AC-438-07**（R-438-06）：`canonical status --json` の `dashboard` の項目が、5つのファイルの有無と `written_at` を示し、そろっていれば `ok`、なければ `missing`、`dashboard.error` があれば `problem` と、`warnings` にそのコードと `details.next_step` を示す。実行の前後で、ファイルと `state.json` が変わらず、偽の `gh` に要求がない。
- **AC-438-08**（R-438-07）：`canonical remove` が、`--yes` なしでは5つのファイルを予定に示すだけで消さず、`--yes` で消す。同じ場所のディレクトリとシンボリックリンクは消さない。
- **AC-438-09**（R-438-08）：`tests/unit/presentation/test_dashboard_board_state.py` で、`board_state` のない項目について、`status`（`done`、`todo`、`doing`、`unknown`、なし、大文字）、`deps`（なし、着手できる、止められている、壊れた値）、選択の有無のすべての組み合わせで、`_issue_ready_board_state` の結果が変更の前の関数の写しと同じである。`tests/unit/presentation/` の今のテスト（`deps-raw` の描画を含む）が変更なしで通る。
- **AC-438-10**（AC-15）：版3の振る舞いを確かめる今のテストが、変更なしで通る。従来モードのリポジトリで `workspace sync` などがダッシュボードを作らない。この Issue が変えた既存のテスト（I-3 の canonical のテストの `dashboards_written` の値など）は、`report.md` に一覧で書く。
- **AC-438-11**：`make lint` と `uv run pytest` が通る。

## 未解決事項

- なし（Epic の文書で決まっていなかった点は、統括の判断で決めた。`plan.md` の「統括の判断」）。
- Epic の AC-16 の「題名を変えた後の周期で…ダッシュボードに出る」は、AC-438-04 で確かめる。実機での時間（変化はおよそ1〜2分）は、I-10 で確かめる。

## 制約・前提

- Epic の目的、Issue の分け方、Issue をまたぐ契約（C1〜C11）を変えない。
- 従来モード（宣言の版3）の処理、`.meta.json` の読み書きのコード、版3の振る舞いを確かめるテストを変えない（AC-15）。
- 本物の GitHub に、ラベル、sub-issue、依存、`spec-dock/canonical` ブランチを作らない。本物の spec-dock のリポジトリで canonical のコマンドを実行しない。利用者の状態の置き場（`~/.local/state/spec-dock/`）、`~/Library/LaunchAgents/`、`~/.config/systemd/user/`、ツールの設定を変えない。見本の元のファイルを消さず、書き換えない。
- 並行の I-5（`iss-00432`）と、`ScopeNode` と書き込みの反映（C10）、`canonical status`、`cli/catalog.py` で衝突しうる。先に `main` に入った方を、後の方が `origin/main` のマージで取り込む（rebase しない）。
