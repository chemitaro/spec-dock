---
種別: レポート（Issue）
ID: "iss-00574"
関連GitHub: ["#574"]
最終更新: "2026-11-05"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

ダッシュボードの状態の印を、利用者が選んだ色と丸の形にそろえ、作業中の印に計画の進み具合と稼働を入れた（R-01〜R-07）。

- 状態の色と形（`core/ui.js`、`app.css`）：着手できる＝深い青の再生の丸、作業中＝鮮やかな緑の区切りの輪、止められている＝黄色の一時停止の丸、不明＝紫の「?」の丸、終わった＝灰色のチェック（今のまま）。色は `app.css` の状態の色の札 `--sd-<状態>`（`-bg`、`-line`、`-ink`、輪の残りの `--sd-track`）だけが持ち、`[data-st]` と、止められている・人が止めているの印（縞、「人 n」、「止める」、「Scope を止めている」、概況の「止められている N」）、不明の箱と知らせ、詳しい画面の表紙と要約の札が、これを使う。期限切れ、PR の閉じた・失敗、critical、マージ待ちの列は変えていない。
- 作業中の輪：Issue は `plan.cue` の手順（dropped を除く）で区切り、done を太い緑（3.6）、残りを細い灰（1.4）で描く。12を超えると弧、手順がない・読めないと外枠だけ。Epic・Initiative は配下の Issue の終わった割合。印の言葉は「作業中（手順 4／8 終わった）」「作業中（配下 1／7 終わった）」。
- 稼働：最後に動いた時刻（`active_at` と `plan.cue` の更新時刻の新しいほう。親は配下も含む）が30分以内なら、次の区切り（すべて終わっていれば中心の丸、外枠だけなら太い輪）を2秒の周期で点滅させる。動かすのは構造の図の箱と枠の頭（輪は19px）、要点、詳しい画面の表紙だけ。30分を超えたら、要点と表紙に「N分（時間・日）動きなし」。`prefers-reduced-motion: reduce` では点滅の重ねを消す。開いたままでも30分の境目で描き直す（`app.js` の `liveUntil`、図の描き直しの鍵）。
- API：構造の API と詳しい画面の API の各 Scope に `progress`（作業中の Issue だけ。`{total, done, doing, todo, dropped, modified_at}`、ほかは `null`）。`application/dashboard_progress.py` が `plan.cue` を型なしの `cue export -e steps` で読み、時刻と大きさで覚える（詳しい画面の API は覚えたものを捨てない）。1つの要求で3秒が上限で、時間切れと `cue` がないときは覚えない。`revision` に作業中の Issue の `plan.cue` の時刻と大きさを加え、手順の書き換えが5秒ごとの更新で届く。

### 仕様から変えたこと（実装中に、ブラウザーの確かめで決めた）

- 区切りの太さを 3.2／2 から 3.6／1.4 に、構造の図の箱と枠の頭の作業中の輪を 15px から 19px にした（15px と 3.2／2 では、終わった区切りと残りの区切りの差と点滅の差が読みにくかった。拡大の写しを参照）。design.cue D-03・D-05 と requirement.cue R-01 の受入の数値を直した。
- 詳しい画面の表紙の理由の札と要約の状態の知らせを、作業中・着手できるも状態の色にした（青の note／accent のままだと作業中の緑とそろわなかった）。design.cue D-02 を直した。

### 0.6.0（次の版）の移行の注記に要る契約の変更

- ダッシュボードの状態の色と形が変わる（上の表）。止められているは赤から黄色に、不明は黄色から紫になる。人のタスクが Scope を止めている印も黄色になる。
- 構造の API（`/api/v1/r/<repo>/structure`）と詳しい画面の API（`…/scopes/<ID>`）の各 Scope に `progress` が足される（画面のための項目で、公開の契約ではない）。`revision` は、作業中の Issue の `plan.cue` の書き換えでも変わる。
- 配布の文書と `static-inventory.json` は変えていない（凡例を説明する配布の文書はない）。

## Verification

### 仕様のレビュー（spec-reviewer opus/high）

- round 1：P1 1件（形の半径の受入と設計の値の食い違い）、P2 4件（縮めた動きで外枠が消える、すべて終わった輪で差が出ない、詳しい画面の API が覚えたものを捨てる、付け替えの漏れ）、P3 2件。すべて直した。
- round 2：合格（P3 1件：S-03 の対象の列挙 → 直した）。

### テスト

- 足したテスト：`tests/unit/application/test_dashboard_plan_progress.py`（T-01、T-02。本物の `cue` の1件を含む）、`tests/unit/application/test_dashboard_progress_api.py`（T-03）、`tests/unit/infra/test_dashboard_state_marks.py`（T-04〜T-07：CSS の値からの WCAG の計算、node の形・輪・時刻、静的）。`tests/fixtures/issue544/marks-golden.json` を新しい形で書き直した（変わったのは4つの状態の形を含む所だけ）。
- 色の差（テストで計算）：明るい表示で、印の色と地の差は ready 5.97〜6.47、doing 4.08〜4.42、blocked 3.96〜4.29、unknown 5.74〜6.22、done 3.39〜3.67（すべて 3:1 以上）。札の文字と札の地は 4.5:1 以上。暗い表示も同じ条件を満たす。

### PC のヘッドレスの Chrome（R-07、T-08）

- 一時の状態の置き場（スクラッチパッドの下、`--state-root`、`XDG_CONFIG_HOME` も一時）と、全部の状態を持つ見本のカタログ（[setup.py](artifacts/20261105t134405z--setup.py)）で `uv run spec-dock dashboard serve --port 18574` を立てた。利用者の常駐のサーバーと `~/.local/state/spec-dock/` は使っていない。Chrome は `--disable-features=MacAppCodeSignClone` で起動し、CDP の `Browser.close` で閉じた（[check.mjs](artifacts/20261105t134404z-04--check.mjs)、[cdp.mjs](artifacts/20261105t134405z-01--cdp.mjs)）。`c050e7bd7` の資源で実施。
- 結果（[result.json](artifacts/20261105t134404z-03--result.json)）：PC・390px × 明るい・暗いの4通りで、図の点滅は動いている Issue（iss-00003 4／8、iss-00008 計画なし、iss-00012 すべて終わった）と親だけで、止まっている iss-00004（2時間）・iss-00009（1時間）にはない。ボード・概況・人のタスクの点滅は0件。要点と詳しい画面の表紙に「2時間動きなし」。動いている iss-00003 の表紙は点滅し、「動きなし」はない。`prefers-reduced-motion: reduce` で重ねの `animation-name` が `none`、不透明度0。ブラウザーのエラー0件、横のはみ出しなし。
- 写し：構造の図 [PC 明るい](artifacts/20261105t134401z--pc-light-graph.png)・[PC 暗い](artifacts/20261105t134401z-01--pc-dark-graph.png)・[390 明るい](artifacts/20261105t134401z-02--390-light-graph.png)・[390 暗い](artifacts/20261105t134401z-03--390-dark-graph.png)、要点 [明るい](artifacts/20261105t134402z--pc-light-panel.png)・[暗い](artifacts/20261105t134402z-01--pc-dark-panel.png)、ボード [PC](artifacts/20261105t134402z-02--pc-light-board.png)・[390](artifacts/20261105t134402z-03--390-light-board.png)、概況 [明るい](artifacts/20261105t134402z-04--pc-light-overview.png)・[暗い](artifacts/20261105t134403z--pc-dark-overview.png)、詳しい画面 [動きなし](artifacts/20261105t134403z-01--pc-light-scope-idle.png)・[動いている（暗い）](artifacts/20261105t134403z-02--pc-dark-scope-live.png)、人のタスク [PC](artifacts/20261105t134403z-03--pc-light-todos.png)・[390 暗い](artifacts/20261105t134404z--390-dark-todos.png)、[箱の印の3倍の拡大（上から明るい：消えた・現れた、暗い：消えた・現れた）](artifacts/20261105t134404z-01--zoom-sheet.png)、[縮めた動き](artifacts/20261105t134404z-02--pc-light-graph-reduced-motion.png)。

- 要点の理由の行の印を直した後（`c3d08dedd`）に同じ確かめをやり直し、すべて合格（[result](artifacts/20261105t135030z--result-c3d08dedd.json)）。

### コードのレビュー（code-reviewer opus/high、約束と仕様の2人、範囲 `b290da02a..c050e7bd7`）

- 約束の面：合格。P2 1件（型なしの `plan.cue` の `status` が配列・辞書だと数え上げで例外になり、構造の API が500になる）→ 文字列のときだけ数え、ほかは todo にした（テストを足した）。P3 1件（`parts.js` の冒頭の説明が古い形のまま）→ 直した。
- 仕様の面：合格（1回目の結果は必須の項目が抜けた機械的な誤りで、同じレビュアーが書き直した）。P2 1件（要点の理由の行の印が外枠だけ）→ `stateMark`（`motion: true`）で描き、静的テストで箱・理由の行・札を確かめるようにした。
- 直しは `c3d08dedd`。`make lint` の誤り（ruff 5件、整形、mypy 2件）も同じコミットで直した。

### 最終品質ゲート（quality-gate-reviewer opus/high、1人。キャンペーン `fqg-iss-00574-1`）

- **合格のコミット：`c3d08dedd`**（範囲 `b290da02a..c3d08dedd`、R-01〜R-07・F-01〜F-02、worktree clean）。観点：functional-correctness、requirements-closure、test-adequacy。ChatGPT の補助の道は使っていない（無効）。
- レビューの道：合格。P0 0件、P1 0件、P2 0件、P3 2件（情報のみ：構造の図の描き直しの鍵 `sig` に動いている ID を入れたことを確かめるテストがない。詳しい画面の API の `prune=False` の配線を HTTP 層のテストで見分けられない。どちらも今の実装は正しい）。覆う範囲は完全。
- 試験の道（同じコミット）：`make lint` exit 0（ruff check、ruff format check、mypy すべて pass）。`uv run pytest` exit 0（3746 passed、7 skipped、30分28秒）。

### PR

- [#577](https://github.com/chemitaro/spec-dock/pull/577)（`main` へ、head `c3d08dedd`、`Refs #574`・`Refs #573`）。作る直前に `origin/main` を取り込み直す必要はなかった（`b290da02a` から進んでいない）。

## Residual Risks / Follow-ups

- マージ待ちの列と札は今のまま（accent の青）で、着手できるの深い青と近い。状態ではないので変えていない（枝の印で見分けられる）。
- 点滅の境目は、画面を開いたままなら5秒ごとの確かめで描き直す。タブが隠れている間は確かめないので、戻ったときに描き直す。
