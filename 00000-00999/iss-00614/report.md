---
種別: レポート（Issue）
ID: "iss-00614"
関連GitHub: ["#614"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー）：round-1 不合格（P1 1、P2 5、P3 1）→ 直した（`review-response.md`）。round-2 合格（P2 1、P3 1）→ 実装担当が迷わないよう直した。round-3 **合格**（P0〜P3 すべて0）。結果 `.workbench/spec-review/iss-00614/round-{1,2,3}.json` と `.check.json`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00614`、reviewed_sha `7f7dd2b1d`）。
- **合格した文書の sha256**：requirement.cue `dcc616ab1dab8dd63ccba859040a815b6c183afe69efda784e9a61f40325e686`、design.cue `92f81b4fe6a2d90107880f1b831d4b68a9f4cd3917aa4b6dc1bf1e60fbb7723b`、plan.cue `a97e7572f502e6cdfe8689e632ddc5decac2b14f08fd1ded19558f724717b168`。

## 実装の記録

- 逸脱 codex-symlink-refusal：impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_508f1a4c0a45、launch codex / gpt-6.1-sol / medium）は chat-scratch の writable root の symlink で手元のコマンドを起動できず、変更なしで止まった。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium（dispatch ctx_3898535b8e3c、launch claude / opus / medium）に切り替え、impl-claude と同じ値なので S-01〜S-05 を1つのセッションにまとめた。
- 開始（impl-claude）：開始のコミット `7f7dd2b1d` で基準 `make lint`（exit 0）と `uv run pytest tests/unit/presentation tests/unit/infra -k dashboard`（266 passed）。既存の失敗なし。記録 `.workbench/implement/iss-00614/start.md`。
- S-01 `80f451988`：`views/allgraph/compose.js`（REPO・bodyWidth・compose）と `tests/js/dashboard_allgraph_compose.mjs`・`tests/unit/presentation/test_dashboard_allgraph_compose.py`（T-01・T-02、10件）。先に書いたテストが module のないことで10件落ちることを確かめてから実装。`uv run pytest tests/unit/presentation/test_dashboard_allgraph_compose.py` 10 passed、`uv run pytest tests/unit/presentation tests/unit/infra -k dashboard` 276 passed、ruff・ruff format・mypy（触れたファイル）pass。
- S-02 `7dabc5013`：`/graph` の道（`parseRoute`、`allGraphPath`）、`ALL_TABS` の3つ、`VIEWS.allgraph`（S-04 までは空の render と dispose）、`title()`、`interceptLinks`、サーバーの `_get`、配る側の `reference_cli.md` の「画面の道」。テスト `tests/unit/infra/test_dashboard_allgraph_route.py`（T-03、9件）を先に書き、7件が落ちることを確かめてから実装。`uv run pytest tests/unit/infra/test_dashboard_allgraph_route.py` 9 passed、`uv run pytest tests/unit/presentation tests/unit/infra tests/unit/application -k dashboard` 434 passed、ruff・ruff format・mypy（触れたファイル）pass。
- S-03 `85d75d0a9`：開始のコミットの資産を `git archive 7f7dd2b1d src/spec_dock/assets/dashboard` で `.workbench/implement/iss-00614/start-assets/` に出し、偽の DOM（`tests/js/fake_dom.mjs`、HTML を要素の木に読み、選び・稼働の印・状態の札まで動かす）と `tests/js/dashboard_graph_golden.mjs` で graph.js を描いた写しを `tests/fixtures/issue614/graph_dom_golden.json`（要求と出力、2回の生成で同じバイト）に残した（入れ子・木 × 全体・いま・これから、focus、片付けの候補と畳んだ塊、選びと path、状態の札、稼働の印の行、保存した実の構造、空と読めない）。その後 `views/graph/draw.js`（descendants・cleanupMap・tally・boxHtml・frameHtml・chipHtml・pos・treeSvgPaths・edgeClass・RANGES・HL・hlCounts・chipsHtml・zoomHtml・rangesHtml・renderLegend）を取り出し、graph.js は描く文脈 `dc()` を作って呼ぶだけにした。写しとの一致（`test_dashboard_graph_golden.py`）は、draw.js の線の class を1文字変えると落ちることも確かめた。ソースの文字列のテスト3つ（orca_views_js の boxHtml・frameHtml・renderLegend、shell_polish の wtMark、state_marks の motion・stateMark）は読むファイルだけを draw.js に移し、文字列と数は変えていない。`uv run pytest tests/unit/presentation tests/unit/infra -k dashboard` 287 passed、ruff・ruff format・mypy（触れたファイル）pass。
- S-04 `e50695091`：`views/allgraph.js`（殻・読み込み・5秒の版の読み・リポジトリごとの配置の覚え（sig）と setTimeout(0) の間・compose による平らな `section.ax-repo` の描画・見出しと段の札・1件1行の警告・選びと横の欄（`repoCtx` と `current()`）・状態の札の合計・稼働の印とエージェントの行（リポジトリごと、2回まで）・拡大と移動・『収める』・`specdockEdgeAudit`・`specdockAllGraphStats`）、`views/allgraph.css`（新しい色の値と札なし）、`_shared/panel.css` の `--pn-w` のセレクターに `[data-view="allgraph"]` を足した（構造の図とボードの値は同じ）。テスト `tests/js/dashboard_allgraph_screen.mjs`・`tests/unit/presentation/test_dashboard_allgraph_screen.py`（T-05〜T-07、15件）を先に書き、module がないことで落ちることを確かめてから実装。`uv run pytest tests/unit/presentation tests/unit/infra -k dashboard` 302 passed、ruff・ruff format・mypy（触れたファイル）pass。
  - 軽い実機の確かめ（受け入れの写しではない。S-06 はタスク担当）：合成の9つの登録の一時の状態の置き場と `uv run spec-dock dashboard serve --state-root … --port 47931 --offline`、headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で 1440・1000・390 × 明・暗 × 3範囲：edgeAudit の total の違反0、横のスクロールなし、『収める』の後に全枠が図の領域に収まる、入れ子と段の札が出る。ブラウザーのエラーは、殻が既定の orca-web（127.0.0.1:8791）の `embed/agent-marks.js` を読もうとして CORS で断られた2種だけ（この画面ではなく殻の既存の動き。S-06 では orca の設定を一時の置き場に向けること）。

## Outcome

## Verification

## Residual Risks / Follow-ups
