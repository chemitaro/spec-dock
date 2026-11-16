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

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー）：round-1 不合格（P1 1、P2 5、P3 1）→ 直した（`review-response.md`）。round-2 合格（P2 1、P3 1）→ 実装担当が迷わないよう直した。round-3 **合格**（P0〜P3 すべて0）。結果 `.workbench/spec-review/iss-00614/round-{1,2,3}.json` と `.check.json`（iss-00614 の worktree、reviewed_sha `7f7dd2b1d`）。
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

## 実機の写し（S-06、タスク担当）

- `23e32e182` を `git archive` から wheel にし、隔離した venv と、この PC の状態の置き場の写し（`.workbench/iss-00614/state`）、`XDG_CONFIG_HOME` の試しの設定（`orca_web.port` 18799）で、`spec-dock dashboard serve --offline --tailscale --port 18614` を立てた。常駐の 47800 と 8791、道具の環境には触れていない。
- 試しの orca（`.workbench/iss-00614/tools/relay_orca.py`、tailnet の 18799）：常駐の orca-web（8791）を GET で読むだけで中継し、CORS の頭だけを足す（エージェントは本物の要約のまま）。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で 1440・1000・390 × 明・暗 × 『これから・いま・全体』の18枚（`.workbench/iss-00614/tools/shoot.mjs`、数字は [result.json](artifacts/20261116t215827z-02--result.json)）。
  - 一覧の API：company-os・spec-dock・orca-web が最上位、housing-lifecycle と input-devices が company-os の子［事業］、taikyohiyou_project が housing-lifecycle の子、generic-mona・tenting-cradle・yubisaki が input-devices の子［プロダクト］。画面の枠の data-depth と見出しの札も同じ。
  - 18枚すべてで、ブラウザーのエラー0、ページの横のスクロールなし、道具の帯と枠の見出しの重なり0、『収める』の後にすべての枠が図の領域に収まる（倍率 1440：12%・6%・2%、1000：10%・5%・2%、390：7%・2%・1%）。
  - 『これから』で9つの枠がすべて出た（実データでは、どのリポジトリにも見える Scope があるか、見える子を持つ入れ物の親 company-os）。『全体』『いま』で箱の数が増え、company-os は入れ物（中の図が空）のまま。
  - 稼働の印：taikyohiyou_project・tenting-cradle・spec-dock（これから）、housing-lifecycle・taikyohiyou_project・tenting-cradle・spec-dock（全体）の箱に出て、対応した worktree のないリポジトリには出ない。
  - 選び：1440 明『これから』で housing-lifecycle の iss-00025 を押すと、横の欄が開き、選ばれた箱は housing-lifecycle の iss-00025 だけ、『詳しい画面』の href が `/r/github.com/chemitaro/housing-lifecycle/scopes/iss-00025?tab=summary`、押すとそのリポジトリの詳しい画面（題名「iss-00025 · 詳しい画面 · chemitaro/housing-lifecycle · SpecDock」）へ移った。
  - 配置の回数（`specdockAllGraphStats`）：各リポジトリ1回の読み込み、配置は1〜2回（2回目はエージェントの行の測り直し）。
- 線の検査（倍率 100%、稼働の印の要約を1回待ってから）と、単体の構造の図との比べ（統括の決定 msg_df4ba7148ea7、[own-compare.json](artifacts/20261116t215827z-03--own-compare.json)）。違反が0でない組だけを挙げる（『これから』はすべての幅で0、ほかの組も0）：

| リポジトリ | 範囲 | 画面の幅（中の幅） | 横断の構造 | 単体の構造の図（同じ中の幅、稼働の印あり） | 新しい違反 |
|---|---|---|---|---|---|
| housing-lifecycle | 全体 | 1440（1344） | boxHits 6 | boxHits 6 | 0 |
| taikyohiyou_project | 全体 | 1440（1312） | overlaps 2 | overlaps 2 | 0 |
| taikyohiyou_project | 全体 | 1000（872） | overlaps 1 | overlaps 1 | 0 |
| taikyohiyou_project | いま | 390（360） | overlaps 8 | overlaps 8 | 0 |
| taikyohiyou_project | 全体 | 390（360） | overlaps 1 | overlaps 1 | 0 |

  明・暗で同じ数。ownHits・diagonal・portShare・failed・missing・markOverflow・drift はすべて0。
- 写し：[1440 明 これから](artifacts/20261116t215825z--allgraph-1440-light-next.png)、[1440 暗 全体](artifacts/20261116t215826z--allgraph-1440-dark-all.png)、[1000 明 いま](artifacts/20261116t215826z-01--allgraph-1000-light-now.png)、[390 明 これから](artifacts/20261116t215826z-02--allgraph-390-light-next.png)、[390 暗 全体](artifacts/20261116t215826z-03--allgraph-390-dark-all.png)、[選んだ箱と横の欄](artifacts/20261116t215827z--allgraph-1440-light-next-selected.png)、[詳しい画面へ移った後](artifacts/20261116t215827z-01--allgraph-detail-after-click.png)。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet の 18614 番の `/graph`（URL は統括への報告で伝えた）。試しの orca は 18799。止め方：`kill $(lsof -tnP -iTCP:18614 -sTCP:LISTEN) $(lsof -tnP -iTCP:18799 -sTCP:LISTEN)`（またはタスク担当・統括に頼む）。

## 次の提案

- **iss-00627（統括が起こす：構造の図で、画面の実寸と配置のずれから線が箱に重なるのを直す）への材料**：
  - 上の表の違反は、横断の構造でも各リポジトリ単体の構造の図（`/r/<repo>/`、入れ子、同じ範囲、見える幅 = 中の幅）でも、同じ数だけ出る。明・暗によらない。
  - 同じ構造・同じ範囲・同じ幅で、node の `routeLayout` と `audit`（DOM なし、稼働の印なし）では、housing-lifecycle と taikyohiyou_project のどの組も違反0（`.workbench/iss-00614/tools/node_audit.mjs`）。違反は DOM から測った四角（`edgeAudit` は箱と枠の実寸を測る）でだけ出るので、画面の実寸と配置の寸法のずれ（housing-lifecycle の boxHits は稼働の印が8つの『全体』、taikyohiyou_project の overlaps は稼働の印が26の範囲）が疑わしい。drift（箱の位置のずれ）は0なので、ずれは高さか線の通り道の側。
  - 参考：taikyohiyou_project を画面の幅 1440（見える幅 1424）で単体の構造の図にすると、node の audit でも overlaps 1（`ownGraph`）。
  - 再現：この PC の状態の置き場の写しで `dashboard serve --offline`、`/r/github.com/chemitaro/taikyohiyou_project/` を見える幅 360（窓 376）・『いま』で開き、稼働の印が出てから `window.specdockEdgeAudit()` → overlaps 8。
- Epic epic-00612 の文書の更新（仕様レビュー round-4 の P2）：Epic の R-08 の受入（edgeAudit の違反0）と D-07 の「最小の倍率の下限も同じ」を、この Issue の変更（単体と同じ数、allgraph の下限 0.002）に合わせ、iss-00627 を Epic の切り分けか依存に入れる。Issue の requirement.cue R-07 の本文の「構造の図と同じ式」も、下限の例外を書き足すとよい（文書の食い違いだけで、動きは D-07 のとおり）。
- 最終品質ゲートの P3（記録だけ）：Scope のあるリポジトリが配置を待つ短い間、警告の行が組み立てに数えられずに「読み込んでいます…」の行と重なりうる（`sizes()` が配置前のリポジトリを loading として warns 0 で渡す）。直すなら、配置前でも warns を渡す。

## Outcome

## Verification

## Residual Risks / Follow-ups
