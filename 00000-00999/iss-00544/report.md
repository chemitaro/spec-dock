---
種別: レポート（Issue）
ID: "iss-00544"
関連GitHub: ["#544"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

第3波（#529・#531・#532）の報告に残った手直し5件を入れた（提供側の変更だけ。配布資産の文書、`static-inventory.json`、版の番号、`migration.md` は変えていない）。

1. **骨組みの格子（R-01）**：`app.css` で `.top`／`.mtabs`／`.notices`／`.main` を `grid-row: 1〜4` に固定した。出ない帯は高さ0の行に残り、`<main>` は常に `minmax(0, 1fr)` の4行目に入る。#532 の `.main[data-view="graph"|"timeline"] { grid-row: 4; }` の回避と、その説明のコメントを消した。
2. **構造の API の `assurance`・`branch`（R-02、R-03、F-01、F-02）**：`application/dashboard_scope_details.py` に `read_structure_facts` と `StructureFactsCache` を足し、`DashboardHttp` が1つの表を持つ。
   - `git worktree list` は構造の要求ごとに1回。ブランチ名がその Scope を指す最初の worktree のブランチ（詳しい画面と同じ `branch_names_scope`）。
   - 保証レベルは `requirement.cue` の `st_mtime_ns` と大きさで覚え、変わらなければ `cue` を走らせない。`cue` の在りかは要る時だけ1回探す。読めなかった値（壊れたファイル）も覚え、時刻か大きさが変われば読み直す。
   - 外の処理は1要求で合わせて3秒。上限の後の Scope と、上限をまたいで読めなかった Scope は `null` で覚えず、次の要求で読む。その要求で見なかった Scope の分は捨てる。表はロックで守る（サーバーは要求を並んで処理するため）。
   - どの読み取りの失敗も、構造の API は 200 で、その項目だけ `null`。
   - 詳しい画面の `scope.assurance`／`scope.branch` は、その要求の `details` から作る（`details.assurance.level`、`details.worktrees.items[0].branch`）。
   - `read_scope_details` の既定の読み手を、呼ばれた時に決める形にした（振る舞いは同じ。テストで差し替えるため）。
3. **印の値の置き場（R-04）**：`core/ui.js` に、全アイコンの形（`parts.js` の `MORE_ICONS` と `marks.js` の `GRAPH_ICONS` を合わせた。同じ名前の9つは同じ形だった）、`STATE_WORDS`（`STATES` の label から作る）、`KIND_LABEL`、`ASSURANCE_LEVELS`、`PR_STATE_WORDS` を置いた。`parts.js`・`logic.js`（`LANES`・`DONE_LANE`・`KINDS` の言葉も）・`marks.js`・`timeline.js` はそこから取る。印の HTML は変えていない（基準のコミット `8ad7ef252` の資源から作った見本 `tests/fixtures/issue544/marks-golden.json` と一致）。構造の図の箱の worktree の印は、Epic R-15 の「作業中なら」に従い、状態が作業中の箱だけに出す（要点の欄のブランチは状態に関わらず出す）。
4. **「見た」の 409（R-05）**：骨組みは `snapshot.fetched_at` があるとき（モデルがあるとき）だけ「見た」を送る。`api.markSeen` は断られても、`fetch` が失敗しても `null` を返す。サーバーの 409 は変えていない。
5. **線の重なり（R-06）**：`views/graph/layout.js` の `routeLayout` の引き直しを最大10回にし、収まらないときは最後の回でなく、`router.js` の `audit` の問題の数が最も少ない回（同じなら早い回）を返す。返す形に `problems` を足した。線の検査のテストの代表のデータに、250件の見本の種 15 と 18 を足した（直す前の「8回・最後の回」では車線が重なる。直す前のコードで赤になることを確かめた）。

### 線の重なりの調べ（手元の私的な構造。テストには入れていない）

- この PC の5つの構造のスナップショット（`~/.local/state/spec-dock/github/...` を読むだけ）で、#532 と同じ表し方の組み合わせ（16通り × 5 と、開いた Epic・Initiative への絞り込み）150通りを検査した（#532 の時点の 171通りから、スナップショットの更新で数が変わった）。
  - 直す前：146/150 が0件。残る4通りは #532 の報告と同じ（housing-lifecycle 入れ子1、taikyohiyou_project 入れ子1・木2）。
  - 直した後：148/150 が0件。housing-lifecycle と taikyohiyou_project の入れ子は0件。taikyohiyou_project の木（終わったもの・すべての線、畳む・畳まないで同じ配置の2通り）は車線の重なりが 8件 → 2件に減ったが残る。
- 直せない理由（木）：木では全 Scope が字下げの1列に並び、線284本の長い縦の線が狭い字下げの通り道を取り合う。広げられる隙間は字下げ1つだけで、広げても深さの違う箱どうしの間は少ししか広がらず、回を重ねても収まらない（16回まで試して悪化した）。直すには木の線の通り道を別に設けるなど、経路の作り方を変える必要がある。
- 試して採らなかったもの：(1) 回数を増やすだけ（10回）→ 別の見本（種 1）で、一度0件になった配置が次の回で崩れた。(2) 寄せが残す数 px の凸を消す処理 → housing-lifecycle の別の組み合わせ（木、入れ子の畳まない）で重なりが増えた。
- 生成の見本 60個（120件・250件 × 種 1〜30）では、直した後も 250件の種 6 の終わったもの・すべての線の2通りに車線の重なり8件が残る（直す前と同じ数）。
- 速さ：線284本の taikyohiyou_project の木で、配置と経路に約2.5秒（収まらない構造では各回で検査を数えるため、#532 の約2.4秒からわずかに増えた。Epic R-13 の3秒以内）。250件の見本（種 532）はテストで1秒以内。

### 0.6.0 の移行の注記（#534）に要る契約の変更

- 公開の契約の変更はない。コマンド、`static-inventory.json`、配布資産の文書、状態の置き場のファイルは変えていない。
- 構造の API（契約にしていない `specdock.dashboard/v1`）の `structure.scopes[].assurance` と `branch`、`scopes/<ID>` の `scope.assurance`／`branch` に値が入るようになった（項目と意味は #532 のまま）。構造の要求ごとに、サーバーがカタログで `git worktree list` を1回と、変わった `requirement.cue` だけ `cue export` を走らせる（合わせて上限3秒、読むだけ）。
- 画面：構造の図とその要点の欄に保証レベルとブランチの印が出る。スナップショットのないリポジトリでは「見た」を送らない。
- 注記の案：「ダッシュボードの構造の図に、保証レベルとこの PC の worktree のブランチの印が出るようになった。」

## Verification

- `spec-dock scope check iss-00544`：誤り0、警告0。
- 仕様のレビュー（spec-reviewer opus/high）：1回目 pass（P0・P1 0、P2 4、P3 1）。P2・P3 は仕様に取り込んだ（締め切りをまたいだ時間切れを覚えない、表のロック、`timeline.js` の import、worktree の印の受け入れ条件、互換性の注記）。`.workbench/spec-review/iss-00544/`。
- テスト駆動：
  - `tests/unit/application/test_dashboard_structure_facts.py`（新規、13関数・14件。カタログの2つの状態はパラメーター）：値、2回目は `cue` を走らせない・`git worktree list` は要求ごとに1回、書き換えた1件だけ読み直す、見なかった Scope を捨てる、壊れたファイルを覚える、例外・`git` の失敗・`cue` がない・カタログがない／決まらない、締め切りの後と締め切りをまたいだ読みを覚えない（時計の差し替え）、HTTP の構造と詳しい画面。先に書いて赤（import の失敗）を確かめた。
  - `tests/unit/infra/test_dashboard_shell_polish.py`（新規、6件）：格子の4行、画面の CSS に `grid-row` がない、値の表が `core/ui.js` だけにある、箱の worktree の印は作業中だけ、印の HTML が基準と同じ（node、`tests/js/dashboard_marks_dump.mjs`）、「見た」はモデルがあるときだけ。先に書いて赤（5件失敗）を確かめた。
  - `tests/unit/presentation/test_dashboard_graph_js.py`：代表のデータに種 15・18 を足した。直す前の `layout.js` で赤（種 15 などで車線の重なり）、直した後に緑。
- PC のヘッドレスの Chrome（CDP、`--disable-features=MacAppCodeSignClone`、`Browser.close` で終了）。一時の状態の置き場（`XDG_STATE_HOME` を `.workbench` の下）でサーバーを立て、利用者の `~/.local/state/spec-dock/` には書いていない（私的な構造の線の検査はスナップショットを読むだけ）。仕組みと結果：[check.mjs](artifacts/20261103t221001z--check.mjs)、[setup.py](artifacts/20261103t221002z--setup.py)、[結果](artifacts/20261103t221002z-01--result.json)。コミット `1aabe40db` で実施（その後の `25d9d420f` は `logic.js`・`timeline.js` の表を `core/ui.js` から作る直しで、値は同じ。node の HTML の比較で確かめた）。
  - R-01：PC（1440×900）と 390px で、構造の図、ボード、時間の軸、詳しい画面、横断の概況の10通りすべてで、`<main>` の高さ ＝ 窓の高さ − 上の帯 − 画面の切り替え − 知らせの帯（PC 788px／844px、390px 668px／788px）、下端が窓の下端。横断の概況の PC は、画面の切り替えと知らせの帯の両方が出ない、直す前に高さ0になる形。写し：[PC のボード](artifacts/20261103t221002z-02--pc-board.png)、[PC の概況](artifacts/20261103t221002z-03--pc-overview.png)、[390px の構造の図](artifacts/20261103t221003z--390-graph.png)。
  - R-05：スナップショットのないリポジトリの構造の図、ボード、時間の軸（PC と 390px）で、JS のエラー0件、「見た」の `POST` 0件。スナップショットのある見本では、開いたときに1回だけ送る。[写し](artifacts/20261103t221003z-02--pc-empty-timeline.png)。
  - R-02・R-04：見本（カタログを本物の Git のリポジトリにし、iss-00002 に `requirement.cue`（standard）と worktree `u/iss-00002`、iss-00003 に strict）で、本物の `cue` と `git` が値を返し、作業中の iss-00002 の箱に保証の2段と worktree の印、止められている iss-00003 に3段だけが出る。詳しい画面に「保証レベル standard」「ブランチ u/iss-00002」。[写し](artifacts/20261103t221003z-01--pc-sample-graph.png)。
  - どの画面でも JS のエラー0件。
- コードのレビュー（code-reviewer opus/high、standards と spec の2人、`1aabe40db`）：両方 pass。standards：P3 1件（dump のコメントの参照先）。spec：P2 1件（report.md が空で S-06 の記録先がない → この report.md に書いた）、P3 1件（`logic.js` の `KINDS`・`LANES`・`DONE_LANE` と `timeline.js` の `KINDS` に言葉の写し → `core/ui.js` から作る形に直した、`25d9d420f`）。`.workbench/code-review/iss-00544/`。
- `make lint` と `uv run pytest`（全体）：最終品質ゲートの節を見る。

## Final Quality Gate

（記入中）

## Pull Request

（記入中）

## Residual Risks / Follow-ups

- 木の表し方で線の多い構造（taikyohiyou_project、線284本）の、終わったもの・すべての線の組み合わせに、車線の重なりが2件残る（上の「線の重なりの調べ」）。木の線の通り道の作り直しは別の Issue で扱う。
- 生成の見本の種 6（250件）の終わったもの・すべての線に、車線の重なり8件が残る（直す前と同じ）。
- CUE の Scope が多いカタログでは、サーバーを立てた後の最初の構造の要求で `cue` を Scope の数だけ走らせる（spec-dock では35件、1件 約10ms）。3秒で切り、残りは次の要求で読む。
- iPhone の Safari の実機での表示は確かめていない（#534 で利用者に頼む）。PC の Safari も未実施。
- `node` のない環境では、新しい印の HTML の比較のテストが飛ぶ（CI では失敗にする）。
