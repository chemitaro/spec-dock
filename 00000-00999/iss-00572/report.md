# 実施報告 iss-00572（#572）

親は epic-00080（#80）。作業メモの 2（`migration.md`）はこの Issue では直さない（0.9.0 のリリースの Issue が行う）。

## 1. 負荷で落ちる時間のテスト
- `test_the_250_scope_structure_routes_within_a_second`：時間を node の CPU 時間（`process.cpuUsage` の user+system）にし、時間を見る組み合わせだけ 3 回のうちの最小を採る。上限 1000ms はそのまま。通常の負荷なしの最大は 275ms。node の呼び出しの上限は 300 秒から 1800 秒へ。
- `test_bootstrap_timeout_keeps_applied_project_files_and_stops_its_child_group`：timeout は Git の事前確認も含めるので、0.1 秒では hook の開始前に切れる。1.0 秒にし、hook の sleep を 2 秒、止まった後の待ちを 1.5 秒にした（確かめる内容は同じ）。
- 負荷の下の確認：`yes > /dev/null` を 40 本（10 コアの 4 倍）走らせ、2 テストとも通った（グラフ 159 秒で通過、bootstrap のファイル全体 33 件が 80 秒で通過）。負荷のプロセスは終了後に `pgrep -x yes` が 0 であることを確かめた。

## 2. ダッシュボードの見た目（写し：`artifacts/screenshots/before|after/`）
写しは headless Chrome（CDP）、一時の状態の置き場で立てたこの worktree のサーバー、PC 幅 1400px と 390px、明るい・暗いで撮った。名前は `a-`（favicon）、`b-`（概況）、`c-`（文書）、`d-`（図）＋`-light|dark-1400|390`。
- (a) `/favicon.ico` の 404：前は SPA の各ページで `404 /favicon.ico` が 1 件（`before/a-*`、`b-*`、`d-*`）。後は 0 件（`after/*` はすべて `no 4xx`）。`assets/dashboard/favicon.svg` を置き、`index.html` の `<link rel="icon">` で指し、`GET /favicon.ico` も同じ SVG（200）を返す。
- (b) Scope が 0 件の札：前は空。後は「Scope はまだありません」（`before/b-overview-*` と `after/b-overview-*`）。構造を読めたときだけ出す（読み込み失敗とは区別）。
- (c) 文書の目次の背景：**統括のブラウザーでの現象は、headless Chrome で再現できなかった**（PC 幅、スクロールの先頭・中・終わり、目次の内側のスクロール、SPA の iframe の中、明るい・暗い。すべて目次は最後までつながって見えた。`before/c-doc-*`）。原因を確かめられないので、配布資産の `ds.css` は変えず、ダッシュボードが返す文書の HTML（CUE、Markdown、失敗のページ）に `<style id="sd-toc-ground">` を足し、`.ds-layout` に目次の幅の背景と縁の線を敷く（PC 幅、画面表示だけ）。`after/c-doc-*` は見た目が変わらないことの確認。**統括のブラウザーで、直った（または直らない）ことの確認が要る。**
- (d) 390px の帯の下の枠の線：狭い幅（`@container app (max-width: 640px)`）で、図の領域を帯の高さ（46px）の下から始め、帯の背景と縁の線をつけた（`before/d-graph-*-390` と `after/d-graph-*-390`）。参考（P3、直さない）：Scope に絞った（focus）状態では帯が 46px より高くなるので、その状態で図を動かすと帯の下に線が見えうる。

## 3. 検証
- 仕様のレビュー：spec-reviewer（opus / medium）、P0/P1 なし、P2 2 件（D-04 は実装に反映、D-02 は据え置き）。sha256：requirement 015f4e1f…、design 18883de5…、plan は後に status だけ更新。
- コードのレビュー：code-reviewer（sonnet / high）、8362aab04、指摘なし。
- 最終品質ゲート：quality-gate-reviewer（opus / high、1 人）。試行 1 は P1（FQG-001：本文に `</head>` があると `<style>` が本文の途中に入る）→ 2ab6a7c37 で直し、テストを足した。試行 2 は 2ab6a7c37 で pass（P3 1 件）。詳細は `.workbench/final-quality-gate/g1/closure.md`。
- `make lint` 合格。`uv run pytest`（全体）：8362aab04 で 3757 passed, 7 skipped。最終コミットでは dashboard と tests/unit の 2033 件が通過。
- 写しの用意のために、サーバーの状態の置き場で company-os の札に「同じリポジトリのクローンが 2 つ」の警告が出る回があった（作業用の登録を作り直した影響。この変更とは無関係）。

## 4. 次の版（0.9.0）の移行の注記に要る契約の変更
- 配布資産（`static-inventory.json` の行）の変更なし。`ds.css`、文書、スキルは変えていない。
- ダッシュボードの HTTP：`GET /favicon.ico`（200、`image/svg+xml`）と `/assets/favicon.svg` が増えた。文書ページ（`/r/<repo>/scopes/<ID>/doc…`）の HTML に `<style id="sd-toc-ground">` が増えた。
- 版の番号と `migration.md` は変えていない。
