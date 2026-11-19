---
種別: レポート（Issue）
ID: "iss-00668"
関連GitHub: ["#668"]
最終更新: "2026-11-19"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー、2人目なし＝standard の既定）：round-1 合格（P0 0、P1 0、P2 3、P3 3）。P2 2件と P3 3件を直し、P2 1件（台本のパス）は反証した（この worktree の `.workbench/spec-review/iss-00668/review-response.md`）。round-2 **合格**（P0 0、P1 0、P2 0、P3 2）。結果は `.workbench/spec-review/iss-00668/round-{1,2}.json` と `.check.json`（reviewed_sha `1cfce6f96`）。
- **合格した文書の sha256**（round-2）：iss-00668 requirement.cue `5113bd4bd1b1e07391c2ebadb6879714851ac5dc9d0bc9c4ea25f3dc67ff8cfa`、design.cue `f50ceb726d52d273acda8ee4a6995233bb912f79ef427a4b678fe6c2e59109cb`、plan.cue `f370395ea237067a1e98339634fe5efb75da9080bb99cb407ca650737ae9926d`。epic-00667 requirement.cue `229267b3dfd8c8821cbda55e49073522d0db377d8f36a245cbb8ed5d443acd19`、design.cue `5647a071523c67a3628d0775303826f54337f652d148d98c158bc9678d12a8de`、plan.cue `35a71f6c6ce08d0aa22007669f37c80b9e97c00176176b52317fd76c12b3fe15`。
- round-2 の P3（止めない。実装担当への申し送り。意味の範囲の読み）：
  1. D-02 手順5の「`range === "next"` のときだけ」は `count`・`countParts` にだけかかる。`idle`（エージェントが0）は見方に関係なく決める（R-04 の薄さと畳みは全体・いまで効く）。
  2. 同じパスの2つ目の worktree の寄せ（D-02 手順4）は、`unscopedItems` が直した居場所も返し（例：`{items, places}`）、`crossPlace` は `placed.places` にも反映する。項目の `worktree` は、寄せたすべての worktree のエージェントを持つ合わせた worktree（`mergedWorktree`）にして、`paintBandMarks` の `soloWorktree` が2つ目のエージェントも描けるようにする。

## 実装の記録

- 開始のコミット `1cfce6f96`（origin/main、#666 の後）。
- 開始のコミットでの基準（impl-sol）：`test_dashboard_structure_facts.py` 14 passed。S-02 の今ある3ファイル（graph_command・allgraph_command・allgraph_compose）84 passed（`test_dashboard_graph_unscoped.py` は新しいので基準なし）。
- S-01（impl-sol、Codex GPT-6.1 Sol / medium）：T-01 を先に書き、未実装の関数・`items` の属性・API の `items` の欠落で落ちることを確かめてから、D-01（`worktree_items`、`StructureFacts.items`、1回の一覧から items、`dashboard_http` の JSON の `items`）を入れて通した。`test_dashboard_structure_facts.py` 19 passed、`test_dashboard_orca_worktrees.py` 込みで 26 passed、変えた4ファイルの ruff check・ruff format --check・mypy 合格。コミット `794033ceb`（Codex の `66d1b9337` の件名を、タスク担当が日本語に直した amend。内容は同じ）。最初の行が bare のとき次の行を主にしないことも確かめた。
- S-02（impl-claude、Claude Opus 5.5 / medium）：T-02 を `tests/js/dashboard_graph_unscoped.mjs`・`tests/unit/presentation/test_dashboard_graph_unscoped.py`（新）に先に書き、`views/graph/unscoped.js` がないこと（ERR_MODULE_NOT_FOUND）で落ちることを確かめてから D-02 を入れて通した（17 passed）。T-03 を `dashboard_graph_command`（`bandRows` の要求）と `dashboard_allgraph_command`（`rows`・`wrap` の場面、`range` を渡す、`groups` の出力）に先に書き、`BAND` の定数・`bandRowHeight` の欠落などで落ちることを確かめてから D-03・D-04 を入れて通した。節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_unscoped.py tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_allgraph_command.py tests/unit/presentation/test_dashboard_allgraph_compose.py` → 107 passed。`make lint` 合格（ruff check・ruff format --check・mypy）。今のテストの期待の直し：札「main のチェックアウト」→「main」（graph_command の2か所と labelWidth の 125→27、allgraph_command の cross）、帯の行の幅に頭の文字 `Unscoped`（allgraph_command の cross の bands の w）、`BAND` の定数に `perLine`・`lineH`。『これから』の線がなくなる分：allgraph_command の keep・childOnly・keepParent を git の一覧つきの構造で『これから』の新しい決まり（組と居場所が空、`commanding` で keep、行の数）に書き直し、sameIds（線の端が別のリポジトリの同じ key に広がらないこと）は『これから』では線がないので、『いま』の畳んだまとまり（両方のリポジトリの `root.f`）で同じ仕組みを確かめる形にした。S-02 の時点で、画面のテスト（`test_dashboard_graph_command_screen.py` の2件・`test_dashboard_allgraph_command_screen.py` の2件）は札の変更と『これから』の keep で落ちる。graph.js・allgraph.js を変える S-03 でまとめて直す（二度直しを避ける）。コミット `3d47ca4fc`。
- S-03（impl-claude、Claude Opus 5.5 / medium）：D-05（graph.js：組がなくても行を描く、『これから』は線なし、`commandKey` に構造と見方、項目・`+N` の押しと詳細の欄、Esc・閉じる・空の場所で閉じる）、D-06（allgraph.js：組がなくても `crossPlace`、`crossKey` に見方、同じ押し）、D-07（command_view.js の `layersHtml` の項目・印・数・折り返しの位置、`renderWorktreePanel`、orca_marks.js の `openWorktreeButton`）、D-08（graph.css）を入れ、T-04 を `tests/unit/presentation/test_dashboard_unscoped_screen.py`（新）と画面の台本（`dashboard_graph_command_screen.mjs` の run ごとの `doc`・`range`・`embed` と行の写し、`dashboard_allgraph_command_screen.mjs` の印・数・詳細の欄の写し）に書いた。T-04 は実装の後に書いたので、S-02 のコミット（HEAD `3d47ca4fc`）の資産を写した場所で同じ台本を走らせ、行の項目（`[data-cmd-wt]`）がなくて落ちることを確かめた（Red の代わり）。今の画面のテストの期待の直し（理由）：構造の図の帯の札「main のチェックアウト」→「main」と、頭の文字 `Unscoped`（53 + 6）と `Primary` の印（38 + 6、構造に git の一覧がないので F-01 で要約の main に印）の分の位置と幅（`test_the_band_shows_its_items`、`test_pressing_the_band_agent_opens_its_chat` の見出し）。『横断の構造』は、画面の既定の見方が『これから』で、『これから』では線を引かなくなったので、線を確かめる場面を `range: "all"` で走らせる（run に見方がないときの既定）。keep の場面は git の一覧つきの構造で、『これから』の新しい決まり（子の数のある Primary で枠が残る、線なし、見える枠の行は idle の Primary）に書き直し、cross の札と位置（頭の文字の分）を直した。節目：`uv run pytest tests/unit/presentation/ tests/unit/infra/ -k "dashboard"` → 581 passed（657 deselected）。途中の回で落ちた4件（横断の画面の写しで足した欄の名前 `open` が開いた状態の欄を上書きした台本の誤り3件、帯の CSS の検査が `margin-right: 6px` を読む1件）を直してからの結果。T-04 は 15 passed。`make lint` 合格。コミット `e8926bf5a`。
- S-04（impl-claude）：`make lint` 合格（ruff check・ruff format --check・mypy）。全体の `uv run pytest` → 4352 passed、7 skipped（34分9秒、HEAD `e8926bf5a`、ログは `.workbench/implement/iss-00668/s04-full.log`）。`static-inventory.json` にダッシュボードの資産は載っていないので変更なし。

## 逸脱と判断

- 2026-11-19 タスク担当：impl-sol（dispatch `ctx_e78d25d6c3ed`、launch.effective gpt-6.1-sol / medium）は、カタログの report.md への書き込み（`OS_ACCESS_DENIED`、Codex の sandbox の writable_roots にカタログがない）と、2回目の Git の書き込み（`.git/worktrees/iss-00668/index.lock` の作成、Operation not permitted）を拒否されて止まった。統括が了承済みの取り決めどおり、設定は変えず、worker を止め、S-02 から Claude Opus 5.5 / medium（impl-claude）が引き継ぐ（`deviation: codex-sandbox-takeover`）。impl-claude は dispatch `ctx_f57065b24d25`、launch.effective claude-opus-5-5 / medium で S-02〜S-04 を担当する。記録の元は `.workbench/implement/iss-00668/start.md`。

- 2026-11-19 impl-claude（S-02、実装の裁量）：
  - `unscopedItems` は `{items, places}` を返す（round-2 P3 の2）。同じパスの2つ目の要約の worktree のエージェントの band の居場所は、項目の `key` に直した写しの `places` で返し、`crossPlace` は各リポジトリの行のこの `places` を自分の `places` に反映する。項目の `worktree` は `mergedWorktree`（P3 の2）。
  - `idle`（エージェントが0）は見方に関係なく決め、`count`・`countParts` だけを『これから』で付ける（P3 の1）。
  - 印と数の幅は `Math.ceil(labelWidth(文字) * 0.8) + BAND.labelGap`（D-03 の式を整数の px に切り上げた）。数の文字も `labelWidth` の下限 24 を通るので、1桁の数は 20 + 6。
  - `+N`（fold）の幅は `2·border + 2·pad + labelWidth("+N")`（エージェントの欄がないので labelGap も足さない）。
  - 行の高さ（R-09）：同じ行の項目は、いちばん高い項目の高さにそろえる（受入「同じ行のほかの項目と枠の帯がその高さに合う」）。`bandModel` の行に `h`、帯の `h` は行の最大。行の `leadTitle` を写す（D-07 の頭の文字の title 用）。
  - `command.js` の `refOf` を `agentRef` として export し、`unscoped.js` が同じ形のエージェントの参照を作る（D-02 の import の範囲の中）。
  - `bandLabel` は、自分のリポジトリの項目の detached（`branch` がなく `head` がある）を `detached @<先頭7文字>`。git の行から札を作るときは、detached の行だけ `head` を渡す。
  - `crossPlace` は、全体・いまでは今の keep の決め方のまま、行は見える（`visibleWith(keep)` の後の）リポジトリだけに作る。『これから』では見えないリポジトリの行を先に作り、`commanding` のものを keep にする。
  - `crossKey` に `range` を足した（D-06。allgraph.js が渡すのは S-03）。

- 2026-11-19 impl-claude（S-03、実装の裁量）：
  - 詳細の欄のエージェントのボタンは `data-wt-agent`（D-07 の `data-cmd-agent` ではない）。チャットを出している間は欄そのものが `data-cmd-agent` を持つので、`closest("[data-cmd-agent]")` が欄の中のどこを押しても当たってしまう（つまみ・閉じるが効かなくなった）ため。
  - 『横断の構造』の `+N` の key は `fold|<リポジトリの鍵>`（帯の項目は行をまたいで key で引くので、枠ごとに分ける）。`unscopedItems` の `fold` のまま返し、`crossPlace` が付け替える。
  - 線の組があって行の項目が0のときも描く（`clearCommand` は項目も組もないときだけ）。
  - 詳細の欄は、開いている間に帯を描き直すたびに描き直す。中身（key・札・印・パス・エージェント・『Orca で開く』の id・テーマ）が同じなら何もしない（『Orca で開く』の script を読み直さない）。項目が行から消えたら閉じる。
  - `+N` の title・aria-label は「エージェントのいない worktree N件」（英語はこの Issue で決めた語だけ、constraints）。詳細の欄の文言（ブランチ・パス・エージェント・なし）も日本語。
  - 項目の角は `border-radius: 14px`（高さ 28px では今の丸と同じ。折り返した高い項目は角の丸い四角）。印と数は 9.2px・太さ 600・余白なしで、幅は模型の推定（`ceil(labelWidth × 0.8)`）を style で渡す。実際の字の幅とのずれは S-05 の実機で確かめる（design の risks）。
  - エージェントのボタンは模型の slot の位置に絶対の位置で置く（`left = slot.x − item.x − 枠 1px`、`top = slot.y − item.y`、高さ 26px）。`cmdAudit` のボタンの中心と slot の中心のずれの測り方（`offsetLeft + clientLeft + offsetLeft`）はそのまま合う。

- 2026-11-19 impl-claude（S-05 の実機の指摘の直し）：詳細の欄に渡す項目は `commandModel` の帯の項目で、その `agents` は模型の slot（`{id, ref, x, y, w, h}`）なので、`renderWorktreePanel` はエージェントの種類・署名・印を `a.ref ?? a` から読む（実機で2人とも『種類不明』になった）。T-04 に詳細の欄のエージェントの種類（`claude`）の確かめを足し、直す前に落ちることを確かめた。

## Residual Risks / Follow-ups
