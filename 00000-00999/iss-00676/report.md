---
種別: レポート（Issue）
ID: "iss-00676"
関連GitHub: ["#676"]
最終更新: "2026-11-20"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## 開始のコミット

`83b8ee95f8fbcc06b601fd5ab3a02018b0995ee4`（origin/main の 0.9.9、worktree はきれい）。

## 診断（2026-11-20、タスク担当）

- 再現：この worktree のソース（0.9.9 と同じ）で、状態の置き場の写しを使い、別のポートでダッシュボードを立てた。orca-web の要約は、CDP の Fetch で中継して読んだ（常駐の orca-web は Origin `http://127.0.0.1:47800` だけを許すため）。CDP で範囲を切り替えて `specdockCmdAudit()` を取った。
  - `/graph`：next は links 0・arcs 0。now と all は links 8・arcs 2。
  - `/r/github.com/chemitaro/spec-dock/`：next は 0・0。now と all は links 7・arcs 1。
- `paintCommand` に一時の計測を入れて確かめた（計測は戻した）。`/graph` の next では、`commandPairs` が8組を返し、`unknown` は false、worktree は52件が対応していた。それでも `crossPlace` の `pairs` は0組だった（`for (const pair of next ? [] : pairs)`）。
- 結論：計算の退行ではない。2つの決定が重なっていた。`/graph` の既定の範囲は epic-00612 で『これから』と決まっている。iss-00668 の決定（統括 msg_e863b639b47f）で、『これから』では指揮の線を引かない。`/r/<repo>/` の既定は『いま』（layout.js の `DEFAULTS`）なので、そちらでは線が出ていた。
- 反証の試み：次の2つを一時的に当てて既存のテストへの影響を数えた（どちらも戻した）。
  - A（`/graph` の既定を『いま』にする）：allgraph の画面のテストが5件落ちる。
  - C（crossPlace の next の分岐を外す）：テストが5件落ちる。
- 本人の決定は B（両方の画面の『これから』で線を引く）。統括の設計の決定は requirement.cue の decisions にある。

## レビュー記録

- 仕様のレビュー：合格。spec-reviewer opus / high、1回目。結果は `.workbench/spec-review/round-1b.json`（1回目の結果のファイル `round-1.json` は、題名の長さの形式の誤りで検査に落ちたので書き直した。機械的なやり直しで、別の回ではない）。P0 0、P1 0、P2 2、P3 1。合格の sha256：
  - requirement.cue `a43c8b1328635d06d8474a0f0553985ff2deb1584c76f359057c21b6a230c7f2`
  - design.cue `f4422b4e12547c1f9b376827f98114ca4ce5ff27896bc17d40d45e3ac5220abe`
  - plan.cue `045d114a1c0149eae356184aea65b6d6cb0c2f78618c881db50e87ff87755208`
- P2・P3 は直さず、受入の読み方を次の「逸脱と判断」に書いた。

## 逸脱と判断

- P2（R-01 の motion・heads）：『いま』と同じ値になることは、『これから』で隠れた Scope を含まない組の入力で確かめる。隠れた Scope の子については、祖先の枠に落ちた分を線の本数で確かめる（T-03 のとおり）。
- P2（F-02 の番号）：この Issue の F-02（F-05 の組み直しの上限を『これから』でも守る）は、『これから』での画面のテストで確かめる。同じ入力のとき描き直さないこと、組み直しが2回までであることを見る。iss-00617 の F-02（unknown のときの見送り）は今のまま確かめる。
- P3（R-04 の『合う』）：`/graph` は全部のリポジトリの組を描く。そのため `/graph` の『いま』の links は、各 `/r/<repo>/` の組を重なりを除いて合わせた数と比べる。実機では、`/graph` の『これから』の links が 0 より多いことと、『いま』と『これから』の差が隠れた Scope の分で説明できることを確かめる。

## 実装の記録（実装担当、claude-opus-5-5 / medium）

### 基準（開始のコミット 83b8ee95f）

- `make lint`：合格（ruff check、ruff format check、mypy）。この worktree で実行。
- `uv run pytest`：開始のコミットの別の複製（スクラッチの `base`、HEAD 83b8ee95f、きれい）で実行。4355 passed、7 skipped、終了コード 0（47分44秒）。既存の失敗はない。

### S-01（横断の居場所と行の項目）

- 先に書いたテスト（T-01・T-02）が、今の実装で落ちることを確かめた：`test_dashboard_allgraph_command.py` 10件、`test_dashboard_graph_unscoped.py` 8件、`test_dashboard_graph_command.py` 1件。落ちた理由は、『これから』で pairs が空、行に子の数がある、指揮していない Unlinked がない、項目の幅に数の足しがある、の4つ（意図どおり）。
- 実装：D-02（`views/allgraph/command.js` の `crossPlace` から `range`・`next` の分岐・`early`・`commanding` を取り除いた）、D-03（`views/graph/unscoped.js` の `range`・`count`・`countParts`・`childCount`・`countTitle`・`commanding`・`UNSCOPED.count`、`views/graph/command.js` の `countWidth`、`views/graph/command_view.js` の `.gx-band-count` の札、`views/graph.css` の `.gx-band-count` の規則を消した）。
- 検証：`uv run pytest tests/unit/presentation/test_dashboard_allgraph_command.py tests/unit/presentation/test_dashboard_graph_unscoped.py tests/unit/presentation/test_dashboard_graph_command.py` 95 passed。`uv run ruff check tests/unit/presentation/`・`ruff format --check` 合格。
- 画面のテスト（`views/graph.js`・`views/allgraph.js` を通すもの）の『これから』の期待は S-02 で直す。S-01 のコミットの時点では、それらの一部が落ちる（S-02 で通す）。コミット `d8ba5e625`。

### S-02（両方の画面）

- T-03 を新しいファイル `tests/unit/presentation/test_dashboard_next_command_screen.py` に書いた（9件）。開始のコミットの別の複製（スクラッチの `red`、HEAD 83b8ee95f）に、このファイルと画面のテストの道具（`tests/js/dashboard_graph_command_screen.mjs`、audit に heads を足しただけ）を写して走らせ、8件が落ちることを確かめた（残りの1件は、動きを減らす設定の CSS が範囲を名指ししないことの静的な検査で、前後とも通る）。この worktree では、S-01 の後に構造の図の4件だけが落ちた（横断の構造の4件は、S-01 の `crossPlace` の直しで先に通っていた）。
- 実装：D-01（`views/graph.js` の `paintCommand` から `drawn` をやめ、全部の組を `placeAgents` に渡す。`unscopedItems` に `range` を渡さない）。`views/allgraph.js` の `crossPlace` の呼び方から `range` を外した。`commandKey`・`crossKey` の `range` は残した。
- 偽の DOM の heads は、CSS がないため 0 にならない（範囲ごとの枠の数で変わる）。T-03 では『これから』と『いま』が同じ値であることだけを見て、heads 0 は実機（S-04）で見る。
- 検証：`uv run pytest tests/unit/presentation/ tests/unit/infra/ -k dashboard` 598 passed、657 deselected。`uv run ruff check tests/unit/presentation/`・`ruff format` 合格。

- コミット `136ad1c8c`。

### S-03（全体の検査）

- `make lint`（HEAD 136ad1c8c）：合格（ruff check、ruff format check、mypy）。
- `uv run pytest`（HEAD 136ad1c8c、全体）：4372 passed、7 skipped、終了コード 0（45分00秒）。基準より 17 件多い（足したテストの分）。
- `src/spec_dock/assets/static-inventory.json`：`assets/dashboard/` の資産は載っていない（`dashboard`・`graph`・`unscoped` の語が0件）。sha256 の直しは要らず、変えていない。
- S-03 はコードを変えていないので、コミットはない（report.md は Git で扱わない）。

### 直したテストの一覧（iss-00668・iss-00617 のテストと、その理由）

理由はどれも、この Issue の決定（『これから』でも線・弧・行・帯を『いま』と同じ規則で出し、子の数の札をやめる。Scope のないリポジトリの枠は iss-00617 R-03 の規則に戻す）。

- `tests/unit/presentation/test_dashboard_allgraph_command.py`（iss-00617 T-01 を iss-00668 が改めたもの）
  - `test_a_repository_with_nothing_shown_is_kept_for_its_coordinator`：『これから』で e の枠が残る理由を、行に数がある項目から、帯に組の親がいることへ戻した。組・居場所・線が出ること、数がないことを見る。
  - `test_a_repository_with_nothing_shown_and_only_a_child_is_not_kept`：子だけのとき、子の端が『ほかの場所』の帯にあり、線が出ることを見る（iss-00617 R-03 のまま）。
  - `test_the_parent_repository_of_a_kept_frame_keeps_its_childs_end`：数の期待を消し、線が出ることを見る。
  - シナリオ `keep`・`childOnly`・`sameIds` の説明の文。node の道具 `tests/js/dashboard_allgraph_command.mjs` は、allgraph.js と同じく `crossPlace` に `range` を渡さない。
- `tests/unit/presentation/test_dashboard_graph_unscoped.py`（iss-00668 T-02）
  - `test_the_words_and_the_fold`：`UNSCOPED.count` がないこと、`childCount`・`countTitle`・`commanding` が書き出されていないことを見る。
  - `test_primary_is_there_without_agents_summary_or_pairs`、`test_unlinked_worktrees_and_a_thin_idle_one`：項目に `count`・`countParts` の欄がないことを見る。
  - `test_next_keeps_primary_and_the_commanding_unlinked_with_counts` → `test_next_has_the_items_and_the_places_of_all_and_now` に置き換えた。
  - `test_all_and_now_show_every_unlinked_without_counts` → `test_every_range_shows_every_unlinked_without_counts`（next を足した）。
  - `test_a_primary_without_children_has_no_count_in_next` → `test_next_keeps_the_unlinked_worktree_directing_nobody`。
  - `test_child_count_counts_each_child_once`、`test_count_title`：関数がなくなったので消した。
  - node の道具 `tests/js/dashboard_graph_unscoped.mjs`：どの範囲でも組を置く。`range` を渡しても結果が変わらないことを確かめるため、わざと渡したままにした。
- `tests/unit/presentation/test_dashboard_graph_command.py`（iss-00668 T-03）
  - `test_badges_and_counts_widen_an_item_and_a_fold_has_no_agents` → `test_badges_widen_an_item_a_count_does_not_and_a_fold_has_no_agents`：古い `count` の欄があっても、項目の幅に数が足されないことを見る。
- `tests/unit/presentation/test_dashboard_unscoped_screen.py`（iss-00668 T-04）
  - `test_the_row_css_uses_only_the_variables`：`.gx-band-count` の規則がないことを見る。
  - `test_next_draws_no_line_and_counts_the_children` → `test_next_draws_the_row_and_the_lines_of_all`。
  - `test_the_cross_next_counts_and_draws_no_line` → `test_the_cross_next_has_the_rows_and_the_lines_of_all`。
- `tests/unit/presentation/test_dashboard_allgraph_command_screen.py`（iss-00617 T-05 を iss-00668 が改めたもの）
  - `test_a_repository_with_nothing_in_next_is_kept_for_its_coordinator`：数の期待を消し、`e-coord>c-own` の線が出ることを見る。runs の既定の範囲の説明の文も直した。
- `tests/unit/presentation/test_dashboard_agent_type_names.py`（iss-00674 T-02、origin/main 6de140261 の取り込みの後、マージのコミット 0955a17bc に対して直した）
  - `test_count_title_names_each_part_from_the_component`：消した。`countTitle` がこの Issue の決定でなくなったため。`agentTypeLabel` そのものの確かめは `tests/unit/infra/test_dashboard_agents_logic_js.py`（iss-00674）に残っている。
  - `test_the_graph_count_title_names_the_kind` → 消して、`test_the_graph_panels_name_the_kind` に『これから』（`named-next`・`plain-next`）を足した。『これから』での名前の表示の確かめが帯の数の札にしかなかったので、worktree の詳細の欄のエージェントの一覧とチャットの見出し・題で確かめる形にした。行に数がないことも見る。
  - `test_the_cross_count_title_names_the_kind` → `test_the_cross_panels_name_the_kind`：横断の構造の『これから』で、帯に数がないこと、worktree の詳細の欄のエージェントの一覧（道具 `tests/js/dashboard_allgraph_command_screen.mjs` の panel に `agentTexts` を足した）とチャットの見出しが表示名になることを見る。
  - もとのテスト（0955a17bc のもの）は、そのコミットの実装で5件落ちる（`countTitle` がない、数の札がない）。直した後は6件が通る。
- 足したテスト：`test_dashboard_next_command_screen.py`（T-03、9件）、`test_dashboard_allgraph_command.py` の `real-*` シナリオの4つのテスト（T-01）。画面の道具 `tests/js/dashboard_graph_command_screen.mjs` は audit に heads を足した。

### 逸脱と気づいたこと（実装）

- 仕様からの逸脱はない。
- 範囲の外：`src/spec_dock/assets/spec_dock/docs/migration.md` の 0.9.9 の節（294 行）に『これから』では線を引かない旨がある。0.9.10 の節の移行の案内は S-04（タスク担当）の範囲なので変えていない。

## 実機の確かめ（S-04、タスク担当、HEAD 136ad1c8c）

- 立て方：`uv build --wheel` で作った wheel（136ad1c8c）を、一時の venv に入れた。本人の PC の uv tool には入れていない。状態の置き場は写しを使い、ポート 47812 で `spec-dock dashboard serve` を立てた。orca-web は常駐の 8791 の要約を読んだ。常駐は Origin 47800 だけを許すので、ヘッドレスの Chrome の CDP の Fetch で中継した。常駐のダッシュボードと orca-web は、止めておらず、設定も変えていない。
- 数（2026-11-20 12:4x、1440 × 明、同じ1回の読み込みで範囲を切り替えた）：

| 画面 | 範囲 | links | arcs | boxOverlaps | edgeOverlaps | heads | motion（phases・ripples） | `.gx-band-count` | specdockEdgeAudit の違反 |
|---|---|---|---|---|---|---|---|---|---|
| `/graph` | これから（既定） | 9 | 3 | 0 | 0 | 0 | 72・5 | 0 | 0 |
| `/graph` | いま | 9 | 3 | 0 | 0 | 0 | 72・5 | 0 | 0 |
| `/graph` | 全体 | 9 | 3 | 0 | 0 | 0 | 72・5 | 0 | 0 |
| `/r/github.com/chemitaro/spec-dock/` | いま（既定） | 4 | 1 | 0 | 0 | 0 | 36・2 | 0 | — |
| `/r/github.com/chemitaro/spec-dock/` | これから | 4 | 1 | 0 | 0 | 0 | 36・2 | 0 | — |

  - 直す前（0.9.9 と同じソース、診断の節）の `/graph` の『これから』は links 0・arcs 0 だった。
  - 組の数は、生きた要約の変化（エージェントの増減）で、測った時刻ごとに 7〜9 の間で変わった。どの回でも、『これから』と『いま』は同じ値だった。
  - 全部の回で、ブラウザーのエラーは0、横のスクロールはなし。
  - この要約では、『これから』で隠れた Scope の worktree の子がなかった。そのため、『これから』と『いま』の本数が同じになった（祖先の枠に落ちる場合は、画面のテスト T-03 で確かめている）。
- 写しの数（1440・390 × 明・暗、どれも『これから』）：
  - `/graph`：links 8・arcs 2、heads 0、boxOverlaps 0、edgeOverlaps 0、エラー0。
  - `/r/spec-dock/`：links 3・arcs 0、heads 0、エラー0。
- 動きを減らす設定（`prefers-reduced-motion: reduce`、`/graph` の『これから』）：`.cl-ph` の `animation-name` が none になり、止まった点線で出る。設定がないときは `sd-cmd-phase` で動く。links は 8、arcs は 2。
- 写し（この Scope の `artifacts/`）。`/graph` は、既定の『これから』のまま、線のある枠まで動かして写した：
  - `20261120t035148z--graph-next-lines-1440-light.png`
  - `20261120t035148z-01--graph-next-lines-1440-dark.png`
  - `20261120t035149z--graph-next-lines-390-light.png`
  - `20261120t035149z-01--graph-next-lines-390-dark.png`
  - `20261120t035149z-02--repo-next-1440-light.png`
  - `20261120t035149z-03--repo-next-1440-dark.png`
  - `20261120t035150z--repo-next-390-light.png`
  - `20261120t035150z-01--repo-next-390-dark.png`
- 気づいたこと：`/graph` の『全体』では、motion の `still` が true になった回があった。これは図が大きいときの止め方（iss-00646 D-03）によるもので、この Issue の変更とは関わらない。

## 移行の案内の文（0.9.10 の節）

- 『これから』でも指揮の線が出ます（#676）。リポジトリの構造の図と『横断の構造』のどちらでも、『これから』の指揮の黄色い点線、同じ箱の親子の弧、動き、波紋、Unscoped の行は、『いま』と同じ規則で出ます。『これから』で隠れた Scope の worktree のエージェントの線は、いちばん近い見える祖先の枠に落ちます。『これから』だけにあった子の数の札はなくなり、『いま』と同じ見え方になります。そのため、既定が『これから』の『横断の構造』を開いたときにも、線が出ます。

## Outcome

## Verification

## Residual Risks / Follow-ups
