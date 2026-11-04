---
種別: レポート（Issue）
ID: "iss-00535"
関連GitHub: ["#535"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

ダッシュボードの Scope の詳しい画面の「文書」のタブで、文書をその場で描いて読めるようにした（epic-00427 の段階2、D-11。Epic R-19・R-25・R-26・F-10）。あわせて #530 の残りの起動し直しの知らせを入れた。

- **CUE の Scope（R-01）**：`GET /r/<host>/<owner>/<name>/scopes/<ID>/doc` が `render_scope` を `design_system_base="/ds/"`、`vendor_base="/vendor/"` で呼んだ HTML を返す。画面は `sandbox="allow-scripts allow-popups"` の枠で示し、新しいタブでも開ける。インターネットは使わない（PlantUML も手元の `/vendor/` で描けることを写しで確かめた）。
- **検査の結果（R-02）**：Scope の API の `details.check`（`status` ok／invalid／failed、誤りと警告のコード・文・ファイル、次の1手）を、タブの上に数と一覧で示す。
- **Markdown の文書（R-03）**：`…/scopes/<ID>/doc/<道>` が `requirement.md`・`design.md`・`plan.md`・`report.md` と、`artifacts/`・`discussions/` の直下の名前に `adr-` を含む `.md` を `wrap_page` に包んで返す。デザインシステムは英字のキーの前書きしか読まないので、題名・道・分類の前書きを付け、文書自身の前書きは YAML の囲みとして本文の頭に残す。
- **計画の進み具合（R-04）**：`details.progress`（`total` は dropped を除く、done・doing・todo・dropped、作業中の手順）を、「概要」と「文書」のタブに帯と数で示す。
- **起動し直しの知らせ（R-05）**：画面は起動時と60秒ごとに `/api/v1/repositories` を読み、`server.restart_required` が true なら知らせの帯の先頭に `SERVER_RESTART_REQUIRED`（入っている版と `spec-dock dashboard serve`）を出す。
- **失敗（F-01）**：`cue` がない・時間切れ・ほかの例外は覚えず、`check.status: failed` と次の1手を示し、仕様の枠は描かない。ほかの札（報告など）とほかのタブは使える。文書の道は理由と次の1手の薄いページを 503 で返す。
- **切り離し（F-02、F-03）**：文書の応答は資料と同じ `_material`（`sandbox allow-scripts allow-popups; frame-ancestors …`、`nosniff`、`no-store`）。許す名前だけを `lstat` と `O_NOFOLLOW` でリンクをたどらずに読む。あいまいなカタログは 409、ほかは 404。
- **覚え**：`ScopeDocuments` が (カタログ, ID) ごとに、Scope の種類と題名と、`requirement.cue`・`design.cue`・`plan.cue`・`explanation.html`・`requirement.md`・リポジトリの型（`<main のチェックアウト>/spec-dock/cue/*.cue`）の `(mtime_ns, size)` を鍵に描画を1つ覚える。5秒ごとの更新で `cue` を動かし続けない。
- **文書**：`reference_cli.md`（提供側と dogfood の写し）の「ダッシュボードのサーバーの契約」に文書の道と起動し直しの知らせを足し、`static-inventory.json` の該当の行の sha256 を更新した（前の値 `891d64db…` を `known_old_sha256` の先頭に追加）。

### 0.7.0 の移行の注記に要る契約の変更

- 画面の道が増える：`/r/<host>/<owner>/<name>/scopes/<ID>/doc` と `…/scopes/<ID>/doc/<道>`（足すだけ。資料と同じ切り離し）。
- `/api/v1/r/…/scopes/<ID>` の `details` に `spec`、`check`、`progress`、`adrs` と、文書ごとの `view` が増える（契約にしない画面の JSON）。
- 前面の `serve` が古い版で動いていると、画面の上の帯が起動し直しを促す。
- `spec-dock/docs/reference_cli.md` の内容が変わる（`installation update` で入れ替わる）。
- 内部：`spec_page._script_safe` を `script_safe` に改名、`SiteRepository` に任意の `checkout`。

### 判断（統括の確認なしに仮で決めたもの）

- ADR は「`artifacts/`・`discussions/` の直下の、名前に `adr-` を含む `.md`」とした（Artifact の `adr` 型の名前に合わせた。ADR でないものを拾うことがあるが読むだけ）。
- 構造の図とボードの補足の1行への進み具合（Epic R-26 の「示せる」）は入れていない（構造の API で全 Scope の `cue` を動かすことになるため）。

## Verification

- 仕様：`spec-dock scope check iss-00535` 誤り0・警告0。仕様のレビュー（spec-reviewer opus/high）round 1 で pass（P0/P1 0、P2 1・P3 3。P2 の覚えの鍵に種類と題名を足し、P3 の文言を仕様に反映）。結果は `.workbench/spec-review/iss-00535/round-1.json`（作業ツリーの .workbench）。
- テスト駆動：`tests/unit/application/test_dashboard_documents.py`（17件、実の `cue` と `DashboardHttp.handle` で T-01〜T-07）。
- コードのレビュー（code-reviewer opus/high、標準と仕様の2人）：どちらも pass。同じ P2（覚えの鍵に `requirement.md` がなく、形式の衝突を古い結果で隠す）を `bc385b273` で直し、テストを足した。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、観点：functional-correctness、requirements-closure、test-adequacy、security-baseline）：結果は下の「ゲート」に書く。
- 画面：一時の状態の置き場（作業ツリーの `.workbench/iss-00535-shots/demo`）で立てたサーバー（127.0.0.1:47935、0.6.0 で起動し installed_version を 0.7.0 にした）を、ヘッドレス Chrome（`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close` で閉じた）で、PC 幅 1440px と 390px、明るい・暗いで12枚写した。各ページでコンソールの誤り0、横のはみ出しなし、文書の枠は `sandbox="allow-scripts allow-popups"`。`cue` を PATH から外したサーバー（47936）で F-01 の表示も写した。利用者の常駐のサーバーと `~/.local/state/spec-dock/` は使っていない。写しは Artifact `artifacts/20261104t070549z--20261104-iss-00535-dashboard-documents-shots.html`。

### ゲート

キャンペーン `iss-00535-g2`（作業ツリーの `.workbench/final-quality-gate/iss-00535-g2/`、Epic の要件の途中の変更を受けて g1 から作り直した）で、`a0ca82979`（origin/main `48e04934d` の取り込み後）に合格。

- レビューの道：pass（coverage complete、P0 0・P1 0・P2 0・P3 3。P3 は下の「Residual Risks」）。
- テストの道 attempt 01：`make lint` 0、`uv run pytest` 1（`test_the_250_scope_structure_routes_within_a_second` が 1014ms で上限 1000ms を超えた。対象の `views/graph/*`・`views/timeline/*` は main と同じで、ロードアベレージ約 40〜60 の負荷による。コードは直さない）。
- テストの道 attempt 02（同じコミット）：`make lint` 0、`uv run pytest` 0（3669 passed, 7 skipped）。
- 結果：`closure.md`。

## Residual Risks / Follow-ups

- 5秒の自動の更新で構造の版が変わると、詳しい画面が描き直され、文書の枠が読み直される（スクロールが先頭に戻る）。
- `#554` も `views/scope.js` と画面の骨組みに手を入れるので、後にマージするほうが取り込み直す。
- ゲートの P3（情報のみ）：リンクになっている CUE のファイル・リポジトリの型の中身の変化を覚えが拾わない／隠した・知らないリポジトリへの文書の道の 404 が資料の見出しを持たない（データもスクリプトも含まない）／Markdown・失敗のページの題名の記号が表紙で解釈される。
- iPhone の Safari での確かめは利用者に頼む。
