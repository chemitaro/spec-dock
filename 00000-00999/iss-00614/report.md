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

- 仕様の変更1（実装の後、統括の決定 msg_df4ba7148ea7、2026-11-17）：R-07 の線の検査の受入を「各リポジトリ単体の構造の図と同じ違反の数、新しい違反0」に改め（違反そのものは iss-00627）、D-07 で allgraph の拡大の下限だけを 0.02 から下げた。round-4（同じレビュアー、reviewed_sha `23e32e182`）：**合格**（P0・P1 なし、P2 1：Epic の R-08 の受入と D-07 の下限の式が変更前のまま、iss-00627 が Epic の slice にない、Issue の R-07 の本文の「同じ式」と下限の変更の記録が decisions にない。Epic の文書は統括の持ち場なので報告に回した）。
- **改めて合格した文書の sha256**：requirement.cue `8da8ae0cf746ddee356eefcf87ce0b8e2eac9061ddd05802b625be0713094312`、design.cue `1c6d1f97854a790277c46a0c5f539a0b3c618dc847ddd5c15d41ed3431ec28e3`、plan.cue `39467c2f0aa38e0aa37ed3095195dceb01c6f619fe13d6b5a0662cb0712bff17`。

## 実装の記録

- 逸脱 codex-symlink-refusal：impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_508f1a4c0a45、launch codex / gpt-6.1-sol / medium）は chat-scratch の writable root の symlink で手元のコマンドを起動できず、変更なしで止まった。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium（dispatch ctx_3898535b8e3c、launch claude / opus / medium）に切り替え、impl-claude と同じ値なので S-01〜S-05 を1つのセッションにまとめた。
- 開始（impl-claude）：開始のコミット `7f7dd2b1d` で基準 `make lint`（exit 0）と `uv run pytest tests/unit/presentation tests/unit/infra -k dashboard`（266 passed）。既存の失敗なし。記録 `.workbench/implement/iss-00614/start.md`。
- S-01 `80f451988`：`views/allgraph/compose.js`（REPO・bodyWidth・compose）と `tests/js/dashboard_allgraph_compose.mjs`・`tests/unit/presentation/test_dashboard_allgraph_compose.py`（T-01・T-02、10件）。先に書いたテストが module のないことで10件落ちることを確かめてから実装。`uv run pytest tests/unit/presentation/test_dashboard_allgraph_compose.py` 10 passed、`uv run pytest tests/unit/presentation tests/unit/infra -k dashboard` 276 passed、ruff・ruff format・mypy（触れたファイル）pass。
- S-02 `7dabc5013`：`/graph` の道（`parseRoute`、`allGraphPath`）、`ALL_TABS` の3つ、`VIEWS.allgraph`（S-04 までは空の render と dispose）、`title()`、`interceptLinks`、サーバーの `_get`、配る側の `reference_cli.md` の「画面の道」。テスト `tests/unit/infra/test_dashboard_allgraph_route.py`（T-03、9件）を先に書き、7件が落ちることを確かめてから実装。`uv run pytest tests/unit/infra/test_dashboard_allgraph_route.py` 9 passed、`uv run pytest tests/unit/presentation tests/unit/infra tests/unit/application -k dashboard` 434 passed、ruff・ruff format・mypy（触れたファイル）pass。
- S-03 `85d75d0a9`：開始のコミットの資産を `git archive 7f7dd2b1d src/spec_dock/assets/dashboard` で `.workbench/implement/iss-00614/start-assets/` に出し、偽の DOM（`tests/js/fake_dom.mjs`、HTML を要素の木に読み、選び・稼働の印・状態の札まで動かす）と `tests/js/dashboard_graph_golden.mjs` で graph.js を描いた写しを `tests/fixtures/issue614/graph_dom_golden.json`（要求と出力、2回の生成で同じバイト）に残した（入れ子・木 × 全体・いま・これから、focus、片付けの候補と畳んだ塊、選びと path、状態の札、稼働の印の行、保存した実の構造、空と読めない）。その後 `views/graph/draw.js`（descendants・cleanupMap・tally・boxHtml・frameHtml・chipHtml・pos・treeSvgPaths・edgeClass・RANGES・HL・hlCounts・chipsHtml・zoomHtml・rangesHtml・renderLegend）を取り出し、graph.js は描く文脈 `dc()` を作って呼ぶだけにした。写しとの一致（`test_dashboard_graph_golden.py`）は、draw.js の線の class を1文字変えると落ちることも確かめた。ソースの文字列のテスト3つ（orca_views_js の boxHtml・frameHtml・renderLegend、shell_polish の wtMark、state_marks の motion・stateMark）は読むファイルだけを draw.js に移し、文字列と数は変えていない。`uv run pytest tests/unit/presentation tests/unit/infra -k dashboard` 287 passed、ruff・ruff format・mypy（触れたファイル）pass。
- S-04 `e50695091`：`views/allgraph.js`（殻・読み込み・5秒の版の読み・リポジトリごとの配置の覚え（sig）と setTimeout(0) の間・compose による平らな `section.ax-repo` の描画・見出しと段の札・1件1行の警告・選びと横の欄（`repoCtx` と `current()`）・状態の札の合計・稼働の印とエージェントの行（リポジトリごと、2回まで）・拡大と移動・『収める』・`specdockEdgeAudit`・`specdockAllGraphStats`）、`views/allgraph.css`（新しい色の値と札なし）、`_shared/panel.css` の `--pn-w` のセレクターに `[data-view="allgraph"]` を足した（構造の図とボードの値は同じ）。テスト `tests/js/dashboard_allgraph_screen.mjs`・`tests/unit/presentation/test_dashboard_allgraph_screen.py`（T-05〜T-07、15件）を先に書き、module がないことで落ちることを確かめてから実装。`uv run pytest tests/unit/presentation tests/unit/infra -k dashboard` 302 passed、ruff・ruff format・mypy（触れたファイル）pass。
  - 軽い実機の確かめ（受け入れの写しではない。S-06 はタスク担当）：合成の9つの登録の一時の状態の置き場と `uv run spec-dock dashboard serve --state-root … --port 47931 --offline`、headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で 1440・1000・390 × 明・暗 × 3範囲：edgeAudit の total の違反0、横のスクロールなし、『収める』の後に全枠が図の領域に収まる、入れ子と段の札が出る。ブラウザーのエラーは、殻が既定の orca-web（127.0.0.1:8791）の `embed/agent-marks.js` を読もうとして CORS で断られた2種だけ（この画面ではなく殻の既存の動き。S-06 では orca の設定を一時の置き場に向けること）。
- S-05 `b9dd24916`：`static-inventory.json` の `spec-dock/docs/reference_cli.md` の sha256 を新しい内容（bd8b72af…）にし、前の値（249f76e9…）を `known_old_sha256` に足した。全体の pytest で落ちた `tests/cli_runtime/test_issue529_dashboard_server.py::test_the_screens_have_the_shell_and_five_slots`（VIEWS の表の文字列）を `allgraph` を含む表に直した。全体の mypy で出たテストの型（`scope_of` の ID が `str | None`）を直した。
- 範囲の拡大 `9ed6680ed`：dogfood の写し `spec-dock/docs/reference_cli.md` を配る側と同じバイトにした。理由：写しと配る側の一致を求める既存のテスト3件（`test_issue550_todo_aggregate.py::test_the_shipped_reference_and_the_help_name_the_new_contract`、`test_issue440_release_0_5_0.py` と `test_issue513_release_0_5_1.py` の `..._dogfood_copy_matches`）が落ちたため。requirement の excludes と依頼書の範囲の外なので問い（msg_6c4ad0ee354c）、統括の了承（msg_21d974dfc4b2、タスク担当経由 msg_635429585fb5）で (a) とした。前例は iss-00613 の `275a5f79c`。
- S-05 の検証（HEAD `b9dd24916`）：`make lint` pass（ruff・ruff format・mypy）。全体の `uv run pytest`：4045 passed、7 skipped、1 failed（`test_the_screens_have_the_shell_and_five_slots`。この実行はテストの修正の前に始めたため、直す前の表の文字列で落ちた）。修正の後に、その1件を含むファイルと写しのテスト（`test_issue529_dashboard_server.py`、`test_issue550_todo_aggregate.py`、`test_issue440_release_0_5_0.py`、`test_issue513_release_0_5_1.py`、`test_issue613_repository_nesting_docs.py`）を HEAD で走らせ 40 passed。1回目の全体の実行は、背景の上限（30分）で46%の時点で止められた（記録 `.workbench/implement/iss-00614/s05-pytest.log`）。
- 修正 `23e32e182`（HEAD 1208670ec から、タスク担当の依頼）：
  - R-07『収める』の判断：D-07 は初めの見え方と『収める』を「graph.js と同じ式」とするが、実データの『全体』の世界（例 12812×38520px）では 1000・390 の幅で fitScale が 0.02 を下回り、graph.js の拡大の下限 0.02 で止まって枠が図の領域からはみ出す。R-07（『収める』の後に全枠が収まる）を満たすため、allgraph.js の `minScale` の下限だけを 0.02 から 0.002 に下げた（`Math.max(0.002, Math.min(0.12, fitScale()))`）。ほかの式と graph.js は変えていない。テスト `test_fit_holds_a_world_that_needs_less_than_the_graphs_least_zoom`（図の領域 300×120 で fitScale が 0.0134 の世界）を先に書き、倍率が 0.02 で止まって落ちることを確かめてから直した。
  - FQG-001（P3）：段の札の `sd-badge` は parts.css の範囲（board・scope・overview・todos・.sd-pn）の外で見た目が当たらなかった。parts.css の範囲に allgraph を足すと構造の図の部品（`.sd-orca` など）にも共有の規則が当たり構造の図と見え方が変わりうるため、allgraph.css に `.gx .ax-tier .sd-badge` として既定の調子の同じ見た目（今の色の札だけ、新しい色の値と札なし）を書いた。テスト `test_the_tier_badges_look_like_the_shared_badges` を先に書いて落ちることを確かめた。
  - 検証：`make lint` pass、`uv run pytest tests/unit/presentation tests/unit/infra tests/unit/application tests/cli_runtime/test_issue529_dashboard_server.py -k dashboard` 465 passed。static-inventory.json は dashboard の資産を持たないので変わらない。

## Outcome

## Verification

## Residual Risks / Follow-ups
