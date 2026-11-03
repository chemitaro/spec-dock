---
種別: レポート（Issue）
ID: "iss-00529"
関連GitHub: ["#529"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

利用者ごとに1つのダッシュボードのサーバー（`spec-dock dashboard serve`）、API、資料の配信と切り離し、`dashboard hide`／`show`／`list`、在りかと隠す印と「見た」の記録、埋め込みの約束（`specdock.embed/v1`）、画面の骨組みと5つの差し込み口を作った。判定は #528 のモデルと要約をそのまま使う。公開のコマンドは 54 → 58。

## Outcome

- サーバー：`runtime/infra/dashboard_server.py`（待ち受け、ロック、在りかの記録、止め方）、`runtime/application/dashboard_http.py`（道筋、見出し、API、資料、「見た」の口。`Request` → `Response` でソケットなしに試せる）、`runtime/application/dashboard_site.py`（登録簿と隠す印の読み直し、最後に読めたモデル、`revision`）、`runtime/presentation/dashboard_api.py`（構造・Scope の JSON と知らせ）、`runtime/infra/dashboard_store.py`（3つのファイルの書き手）、`runtime/infra/dashboard_network.py`（`tailscale ip -4`、`tailscale status --json`）、`runtime/infra/dashboard_assets.py`。
- コマンド：`runtime/application/dashboard_commands.py`。`serve` と `list` はチェックアウトなしで動き、版3のチェックアウトの中では、ほかのコマンドと同じく `CANONICAL_NOT_MIGRATED` で止まる。
- 画面：`src/spec_dock/assets/dashboard/`（wheel に入る。`static-inventory.json` には入れない）。骨組みは `index.html`、`app.css`（d2 のトークン）、`app.js`、`core/{api,embed,route,topbar,ui}.js`。

### #531・#532 が画面を足す差し込み口

- `views/index.js` の表 `VIEWS = {graph, board, timeline, scope, overview}` を骨組みが読む。#531 は `views/board.js`、`views/scope.js`、`views/overview.js`、#532 は `views/graph.js`、`views/timeline.js` を書き換えるだけで足せる（骨組みと表は触らない）。CSS は各モジュールの `styles: ["/assets/views/<名前>.css"]` に書けば、最初に出すときに1回読む。
- 形：`export default {id, title, icon, styles?, render(root, ctx), dispose?()}`。`ctx = {repository, route: {view, repository, scope, params, embed, path}, data（構造の JSON）, scope（詳しい画面の JSON）, repositories, embed, navigate(path), href(path)}`。骨組みはデータか道が変わるたびに `render` を呼ぶ。同じリポジトリの中の移動は `ctx.navigate` か `<a data-nav>`（1つのページの中、比べる元を保ち、`seen` を送り直さない）。`ctx.href` は `embed=1` を引き継ぐ。
- 部品：`core/ui.js` の `esc`、`ic`（アイコン）、`stateIcon`、`chip`、`STATES`、`ago`。共通の CSS（`.ds-docid`、`.st-ico`、`.chip`、`[data-st]` の色）は `app.css` にある。
- 構造の API の形（`structure`、`scopes/<ID>`）は契約にしていない。項目が要れば `presentation/dashboard_api.py` に足してよい（例：このPCの worktree のブランチ、保証レベル。今は持っていない）。検索の枠は上の帯の `#search-slot`（中身は #531）。

### 0.6.0 の移行の注記（#534）に要る契約の変更

- 増えたコマンド4つ：`dashboard serve [--port N] [--tailscale]`、`dashboard hide [REPOSITORY]`、`dashboard show [REPOSITORY]`、`dashboard list`（公開 58）。既定の番号 47800、既定の待ち受けは `127.0.0.1` だけ。
- 状態の置き場の新しいファイル：`<state_root>/dashboard/server.json`（`specdock.dashboard-server/v1`）、`repositories.json`（`specdock.dashboard-repositories/v1`）、`seen.json`（`specdock.dashboard-seen/v1`）、`server.lock`。リポジトリ、カタログ、登録簿には書かない。
- 新しい契約：画面の道 `/r/<host>/<owner>/<name>/scopes/<ID>` と `?embed=1`、`/api/v1/repositories` と `/api/v1/r/…/{summary,structure,scopes/<ID>,revision}`、`POST …/seen` の守り、資料の `sandbox` と `frame-ancestors`、`/ds/` と `/vendor/` だけの CORS、postMessage `specdock.embed/v1`。`reference_cli.md` の「ダッシュボードのサーバーの契約」に書いた。

### 作業者の判断（仕様の decisions にも書いた）

- 同じリポジトリのクローンが2つ登録されているときは、構造は配り、資料の道だけを 409 で断る。
- リポジトリの切り替えはページの読み込み直し。
- 横断の概況（`/`）は差し込み口に、表示中のリポジトリへのリンクだけの仮の中身を置いた（#531 が作る）。
- 隠す印が読めないときは隠したものを出さない：一度読めていればその印を保ち、一度も読めていなければ全リポジトリを隠し、`dashboard list` と `/api/v1/repositories` の `marks_unreadable` で知らせる（コードのレビューの指摘で直した）。
- 読めないスナップショットの要約の API は、CLI と同じく 503（`DASHBOARD_SNAPSHOT_UNREADABLE`）。画面は構造の API で最後に読めたモデルを示す。

## Verification

- `spec-dock scope check iss-00529`：誤り 0、警告 0。
- 仕様のレビュー（spec-reviewer opus/high）：1回目で pass（P0・P1 なし、P2 3件、P3 3件）。P2 の「隠す印が読めないと隠したものが出る」は実装で扱った。`.workbench/spec-review/iss-00529/round-1.json`。
- コードのレビュー（code-reviewer opus/high、standards と spec の2人、372c1e293）：両方 pass（P0・P1 なし）。P2 3件、P3 2件をすべて直した（32804ee42）。`.workbench/code-review/iss-00529/`。
- 新しいテスト：`tests/unit/infra/test_dashboard_store.py`、`tests/unit/application/test_dashboard_http.py`、`tests/cli_runtime/test_issue529_dashboard_server.py`（番号0の実サーバー、子のプロセスの `serve` と SIGTERM、二重起動、使われている番号、Tailscale、hide/show/list、wheel に画面が入る）。コマンドの数を縛るテストを 58 に直した。
- PC のブラウザー（ヘッドレスの Chrome、CDP、`--disable-features=MacAppCodeSignClone`、`Browser.close` で終了）。サーバーは一時のディレクトリの状態の置き場（`XDG_STATE_HOME=/private/tmp/iss529-state.*`）で立て、利用者の `~/.local/state/spec-dock/` は使っていない。仕組みと結果は Artifact：[check.mjs](artifacts/20261103t180658z--check.mjs)、[setup.py](artifacts/20261103t180658z-01--setup.py)、[parent.py](artifacts/20261103t180659z--parent.py)、[結果1](artifacts/20261103t180659z-01--result-1.json)、[結果2（レビューの直しの後）](artifacts/20261103t181500z--result-2.json)、画面の写し [PC のボード](artifacts/20261103t180659z-02--01-board-pc.png)、[古い知らせ](artifacts/20261103t180659z-03--02-stale-notice-pc.png)、[埋め込み](artifacts/20261103t180659z-04--03-embed.png)、[390px・暗い表示](artifacts/20261103t180659z-05--04-phone-dark.png)。
  - 骨組み：上の帯（印、リポジトリの切り替え、3つの画面の切り替え、変化の数、「2分前に取得」）と空の枠が出る（R-13）。
  - 同じリポジトリの中の移動は1つのページの中（目印が残る）で、`seen.json` の記録は1件のまま（R-09）。
  - 自動の更新：開いたままスナップショットを書き換えると、7秒後に再読み込みなしで Scope の数（3 → 4）と変化の数（0 → 1）が新しくなる（R-06）。
  - リポジトリの切り替え：メニューから o/s へ移り、30分を超えて古いことの知らせ（「構造が3時間前から更新されていません」と次の1手）が帯の下に出る（R-03、R-11）。
  - 資料：起点が `null`、`localStorage`・Cookie が SecurityError、API の `fetch` と「見た」の `POST` が読めない（TypeError）、`/ds/ds.css` は読め、相対の `../../../design-system/ds.css` の写しが効く。画面から枠に入れた資料の `contentDocument` は読めない（R-05、F-06）。
  - 埋め込み：親 `127.0.0.1:18629`、子 `localhost:<番号>` の別の起点で、`hello` → `ready`（画面の題名つき）→ `navigated`。子は印とリポジトリの切り替えを隠し、画面の切り替え3つを残し、リンクは `?embed=1` を引き継ぐ。親の `navigate` でボードへ移り、親の URL が `navigated` で追従、`theme` で暗い表示。きょうだいの枠の偽の `hello` と、許していない起点の `hello` を無視し、`hello` の前は何も送らない。`?embed=1` のない画面は別の起点の枠に出ない（R-10）。
  - hide/show：`dashboard hide o/s` の後、概況から消え、直接の道は戻すコマンドの案内だけ。`show` で戻る（R-08）。
  - 幅 390px（暗い表示）：6つの道で `scrollWidth` 390、画面の切り替えは下の段に移る（R-13）。
- 後始末：試しのサーバーと親と Chrome を止めた。止めた後 `server.json` は消え、番号の待ち受けと `remote-debugging-port=19529` の Chrome は残っていない。
- `make lint` と `uv run pytest`（全体）：最終品質ゲートの節を見る。

## Final Quality Gate

- 合格のコミット：`32804ee4262d09e3876c0c7925b8b02d7ba3f0c5`（作業ツリーは clean、試行1回）。記録は `.workbench/final-quality-gate/iss-00529-g1/`（`campaign.json`、`closure.md`、`attempts/01/`）。
- レビューの側：quality-gate-reviewer（opus/high、1人）。観点は functional-correctness、requirements-closure、test-adequacy。pass（P0 0、P1 0、P2 0、P3 3、網羅は完全）。
- テストの側：`make lint` 終了コード0（ruff check、ruff format check、mypy すべて pass）、`uv run pytest` 終了コード0（3443 passed、7 skipped、25分14秒）。どちらも同じコミット。
- P3（情報。直さない）：(1) 止める途中に2回目の SIGTERM か Ctrl-C を受けると、片付けの前にシグナルの扱いを既定に戻しているため `server.json` が残ることがある（`pid` が生きていないので古い記録と見なされる）。(2) `--port 80` で起動すると、番号を省いた `Host` と `Origin` を断る。(3) REPOSITORY を渡した `dashboard hide`／`show` は、版3のチェックアウトの中でも止まらずに印を書く（`dashboard summary` と同じ扱い）。
- 手前の全体のテスト：最初の全体の実行で、全コマンドを1回ずつ動かす2つのテストと版3で止まるテストが落ち、`serve`／`list` が版3のチェックアウトの中で `CANONICAL_NOT_MIGRATED` で止まるように直した（372c1e293 に含む）。

## Pull Request

- PR #540（https://github.com/chemitaro/spec-dock/pull/540）、head `32804ee4262d09e3876c0c7925b8b02d7ba3f0c5`。CI（Provider CI の Actions）は観測できた範囲で PASS、GitHub のマージの可否は READY（2026-11-03T18:58:53Z の観測）。マージと `work finish` は統括が行う。

## Residual Risks / Follow-ups

- iPhone の Safari での表示と埋め込み（指の操作を含む）は確かめていない。#534 で利用者に頼む。PC の Safari も未実施。
- 開いたままでの「何分前」の数え直しは JavaScript を読んで確かめただけで、ブラウザーでは1分を超える待ちを確かめていない。
- 常駐（`dashboard service`、版の更新の後の起動し直し）は #530。前面の `serve` は版の更新を知らせない。
- 資料の HTML は `ds-vendor-base` を持たないと図の部品を CDN から読もうとする（Epic R-24 の画面の側は #531、文書の描画は #535）。
- 手元の確かめで、`uv run spec-dock dashboard serve` を `pkill -TERM`（`uv` と子の両方に届く）で止めたとき、`server.json` が消えずに残った（原因は確かめていない）。インストールした `spec-dock` に直接 SIGTERM を送ると、正しく止まって消える（テスト T-12）。残った記録は `pid` が生きていないので、読む側が古いと見なす。
- infra の `dashboard_server.py` が application の `DashboardHttp` と `DashboardSite` を呼ぶ（Epic D-02 の置き場に従った。infra から application を呼ぶ前例は `git_cli.py` などにある）。
