package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"状態の色を、状態の色の札の1か所で決め、すべての所がそれを使う",
	"作業中の印に、進み具合と稼働を、重い処理を増やさずに入れる",
	"一覧では動かさず、図と要点と詳しい画面でだけ動かす",
]

current: "状態の色は `app.css` の `[data-st]` が DS の意味の色を借りる。止められているの縞と人のタスクの印は `--ds-danger` を直接使う。印の形は `core/ui.js` の `STATES` の固定の SVG。構造の API に計画の進み具合はなく、詳しい画面だけが文書の描画から `details.progress` を持つ。"

target: "状態の色の札 `--sd-<状態>` を `app.css` に置き、`[data-st]` と状態を表すすべての所がそれを使う。`core/ui.js` の `stateIcon(state, label, opts)` が、進み具合と稼働を受けて作業中の輪を描く。構造の API と詳しい画面の API は、作業中の Issue の `progress` を、覚える仕組みつきで返す。"

design: {
	"D-01": {
		title: "状態の色の札（`app.css`）"
		text: """
			`:root` に、5つの状態の `--sd-<状態>`（印と帯）、`--sd-<状態>-bg`（札の地）、`--sd-<状態>-line`（札の枠）、`--sd-<状態>-ink`（札の文字）を、明るい表示と暗い表示（`prefers-color-scheme` と `data-theme` の2か所、今の形と同じ）で置く。作業中には残りの区切りの `--sd-track`（`--ds-border-2`）も置く。

			| 状態 | 明るい：印／地／文字 | 暗い：印／文字 |
			| --- | --- | --- |
			| ready | `#2457c5` / `#edf2fc` / `#1d469f` | `#6f9dff` / `#a8c3ff` |
			| doing | `#0b8a4a` / `#e7f6ee` / `#0a6b3a` | `#3ddc84` / `#7ce8ab` |
			| blocked | `#a86e00` / `#fff6dc` / `#7a5000` | `#ffc93c` / `#ffd978` |
			| unknown | `#7048c0` / `#f3effc` / `#5b37a6` | `#b79bff` / `#d2c0ff` |
			| done | 今の `--ds-faint`、`--ds-tip-*` | 同じ |

			暗い表示の地と枠は、印の色の 10%／28% の透明（今の DS と同じ作り）。`[data-st="<状態>"]` は `--st`、`--st-bg`、`--st-line`、`--st-ink` をこの札から取る。止められている印の中の2本と、終わったのチェックは、地の色（`--ds-bg`）で抜く（今の `.on` と同じ）。
			"""
		satisfies: ["R-01", "R-02"]
	}
	"D-02": {
		title: "状態の色を使う所の付け替え"
		text: """
			- `views/_shared/parts.css`：`.sd-bar i[data-st="blocked"]` と `[data-st="blocked"].sd-card` の縞を `--sd-blocked` に。`.sd-hm`（人 n）を `--sd-blocked-*` に。
			- `views/graph.css`：`.gx-box[data-st="doing"]` の地と枠を `--sd-doing-bg`／`--sd-doing-line` に。`.hm`（人 n）を `--sd-blocked-*` に。
			- `views/overview.js`：「止められている N」の札を `data-tone="blocked"` にする。
			- `views/graph.css`：`.gx-box[data-st="unknown"]` の地と枠を `--sd-unknown-bg`／`--sd-unknown-line` に。
			- `views/board.js`：不明の知らせを `data-tone="unknown"` にする。
			- `views/todos.css`：`.td-blocks`（止める）を `--sd-blocked-ink`／`--sd-blocked` に。
			- `views/todos.js`：「Scope を止めている」の札を `data-tone="blocked"` にし、`parts.css` に `blocked` の札の色を足す。
			- `views/scope.js`：表紙の理由の札と要約の状態の知らせの `data-tone` を、終わった以外はその状態の名前（`blocked`、`unknown`、`doing`、`ready`）にする（今は danger、warning、note、accent）。`views/_shared/parts.css` の `.sd-badge` と `.sd-callout` に、4つの状態の色を足す。
			- 期限切れ、PR の閉じた・失敗、critical、マージ待ちの列は変えない。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "印の形と作業中の輪（`core/ui.js`）"
		text: """
			- `STATES` の形：ready＝輪（半径8.6、線2.4）と中の三角。blocked＝塗った丸（半径9.6）と `.on` の2本の縦の棒。unknown＝輪と `?`（線と点を印の色で）。done＝今のまま。doing＝輪の外枠（`progressRing` の既定）。
			- `progressRing({done, total} | null, {live})`：中心 (12, 12)、半径8.6。
			  - total が1〜12：total 個の区切り（区切りの間に 0.32 ラジアンの隙間）。i < done は `--st` の太い線（3.6）、ほかは `--sd-track` の細い線（1.4）。19px の箱でも太さの差で読めるよう、差を大きく取る。live かつ done < total なら、i = done の区切りに、太い線の重ね（`class="sd-nx"`）を足す。live かつ done = total なら、中心に半径3の塗った丸の重ね（`class="sd-nx"`）を足す。
			  - total が13以上：`--sd-track` の細い輪（1.4）と、done／total の弧（太い線）。live かつ done < total なら、弧の先から 1／total の長さの重ねの弧（`class="sd-nx"`）を足す。done = total なら区切りと同じく中心の丸。
			  - null か total が0：`--st` の外枠（線2.4）だけ。live なら、外枠の上に太い線（3.6）の輪の重ね（`class="sd-nx"`）を足す（外枠そのものは点滅させない）。
			  - 重ねは、どの場合も別の要素で、`.sd-nx` だけが点滅する。名前は、構造の図の絞り込みの釦の `.gx .nx` と重ならないよう `sd-nx` にする。重ねの色は `--st`（`stroke`／`fill` に直接書く）。
			- `stateIcon(state, label = true, opts = {})`：`opts.progress` と `opts.live` を受け、doing のときだけ `progressRing` を描く。`aria-label` は doing で数があれば「作業中（手順 4／8 終わった）」。Epic・Initiative は「作業中（配下 2／5 終わった）」（`opts.unit`）。live なら `data-live="1"` を SVG に付ける。
			- `chip(state, opts)` も同じ `opts` を `stateIcon` に渡す。
			- 純粋な関数を足す：`scopeProgress(scope, byId)`（Issue は `scope.progress` の `{done, total}`、Epic・Initiative は配下の Issue の数え上げ。作業中でなければ null）、`movedAt(scope, byId)`（D-04 の時刻、ミリ秒。分からなければ null）、`LIVE_MS = 30 * 60 * 1000`、`isLive(moved, now)`、`idleWords(ms)`（「N分動きなし」「N時間動きなし」「N日動きなし」。分は60未満、時間は48未満）、`stateMark(scope, byId, {now, motion})`（`motion` が真のときだけ live を渡す。一覧は偽で呼ぶ）。DOM を使わない。
			"""
		satisfies: ["R-01", "R-03", "R-04", "R-05", "F-02"]
	}
	"D-04": {
		title: "最後に動いた時刻と30分の境目"
		text: """
			- `movedAt`：Issue は `active_at` と `progress.modified_at` のうち読める最も新しい時刻。Epic・Initiative は、自分と配下のすべての Scope のそれの最も新しいもの。どれも読めなければ null（F-02：点滅なし、言葉なし）。
			- 骨組み（`app.js`）：構造を読んだとき、作業中の Scope のうち動いているものの「30分の境目」（movedAt + 30分）の最も早い時刻を `state.liveUntil` に持つ。5秒ごとの確かめで `revision` が同じでも、今がそれを過ぎていれば描き直す。
			"""
		satisfies: ["R-05", "F-02"]
	}
	"D-05": {
		title: "点滅（CSS）"
		text: """
			`app.css` に `@keyframes sd-next { 0%, 100% { opacity: .15 } 50% { opacity: 1 } }` と `.st-ico[data-live="1"] .sd-nx { animation: sd-next 2s ease-in-out infinite; }` を置く。`.st-ico .sd-nx` は既定で `opacity: .15`（重ねは live のときだけ描く）。`@media (prefers-reduced-motion: reduce) { .st-ico .sd-nx { animation: none; opacity: 0; } }`（重ねだけが消え、外枠と区切りは残る）。大きさは、構造の図の箱と枠の頭の作業中の輪だけ 19px にし（ほかは今の 15px）、太い区切り（3.6）と細い区切り（1.4）の差で読めるようにする。
			"""
		satisfies: ["R-05"]
	}
	"D-06": {
		title: "画面への組み込み"
		text: """
			- 構造の図（`views/graph.js`）：箱と枠の頭は `M.stateMark(s, byId, {now, motion: true})`。要点の札と理由の行は `motion: true`、作業中で動いていなければ、理由の行の後に「N分動きなし」（`.pn-idle`）。凡例は進み具合の例（`progressRing({done: 3, total: 8})`、動かない）を作業中に使う。数の印（`counts`、`nx` の絞り込みの釦）は形だけ（動かない）。
			- 詳しい画面（`views/scope.js`）：表紙の札は `motion: true` と「N分動きなし」（`.sd-idle`）。要約の作業中の行は形だけ。
			- ボード、概況、検索の候補、人のタスク、時間の軸：`motion: false`（形と数は出す、点滅なし）。ボードのカードと列見出しの作業中は進み具合の輪（動かない）。
			- `views/_shared/parts.js` は `stateMark` を書き出す。`views/graph/marks.js` は `stateMark` と `progressRing` を `core/ui.js` から書き出す。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-05"]
	}
	"D-07": {
		title: "計画の手順の読み取り（`application/dashboard_progress.py`）"
		text: """
			- `read_plan_steps(directory, *, timeout, tool) -> dict | None`：`cue export --out json -e steps plan.cue`（`cwd` は Scope のディレクトリ）。結果が辞書でなければ、または `cue` が誤りを返せば None。
			- `plan_counts(steps) -> {total, done, doing, todo, dropped}`：`dashboard_documents.plan_progress` の数え方を使う（`doing_steps` は返さない）。手順が空なら None。
			- `PlanProgressCache`：カタログごとに `{ID: (plan.cue の st_mtime_ns, st_size, counts | None)}`。ロックで表の読みと差し替えを守る。その要求で見なかった Scope の分は、`prune=True`（構造の API）のときだけ捨てる。
			- `read_plan_progress(site, scope_ids, cache, *, prune=True, timeout=3.0, clock, steps_reader, cue_locator) -> {ID: progress | None}`：`scope_ids` は作業中の Issue だけ（呼ぶ側が選ぶ）。カタログがなければ全部 None。`plan.cue` を `lstat` し、通常のファイルでなければ None。覚えた (時刻, 大きさ) が同じなら覚えた値。違えば締め切りの前に読み、読めた数（なければ None）を覚える。締め切りの後、`cue` がない、読み終えたときに締め切りを過ぎて読めなかったものは None で覚えない。例外はその Scope の None。値には `modified_at`（`st_mtime` の UTC、秒まで）を足す。
			- 構造の API（`dashboard_http.py` の `structure`）：`model.scopes` のうち `kind == "issue"` かつ `state == "doing"` の ID で `read_plan_progress` を呼び、`structure_document(..., progress=…)` に渡す。詳しい画面の API（`scopes/<ID>`）も、その1つの ID が作業中の Issue なら同じキャッシュで `prune=False` で読む（ほかの Issue の覚えた値を捨てず、その1件だけを足すか差し替える）。
			- `presentation/dashboard_api.py`：`scope_item(..., progress=None)` が `"progress": progress.get(ID)` を入れる。`structure_document` と `scope_document` に `progress` を足す（既定 None で `null`）。
			"""
		satisfies: ["R-06", "F-01"]
	}
	"D-08": {
		title: "`plan.cue` の書き換えを `revision` に入れる（`dashboard_site.py`）"
		text: "`DashboardSite._revision` の部品に、モデルの作業中の Issue の `<カタログ>/<区切り>/<ID>/plan.cue` の (時刻, 大きさ) の組を足す（`lstat` だけ。カタログがなければ None）。作業中の Issue は多くても数十なので、5秒ごとでも軽い。"
		satisfies: ["R-06"]
	}
	"D-09": {
		title: "写しの撮り方"
		text: "一時のディレクトリに状態の置き場とカタログと見本のスナップショット（作業中の Issue の `plan.cue` を含む）を作り、`spec-dock dashboard serve` 相当のサーバーを一時の置き場で立てる。ヘッドレスの Chrome（`--disable-features=MacAppCodeSignClone`、終わりは CDP の `Browser.close`）で、PC 幅と 390px、`prefers-color-scheme` の明るい・暗いをエミュレーションして撮る。撮った PNG は Scope の `artifacts` に `artifact import file` で入れ、report.md から参照する。"
		satisfies: ["R-07"]
	}
}

compatibility: "構造の API と詳しい画面の API に `progress` が増える（画面のための項目で、公開の契約ではない）。`revision` が `plan.cue` の書き換えでも変わる。配布の文書は変えない（凡例を説明する配布の文書はない）。次の版の移行の注記：ダッシュボードの状態の色と形が変わる（着手できる＝青の再生の丸、作業中＝緑の区切りの輪、止められている＝黄色の一時停止の丸、不明＝紫の ? の丸）。"

risks: [
	"作業中の Issue が多いカタログで、初回の要求の `cue` が3秒を超える：残りは null で覚えず、次の要求で読む（F-01）。",
	"点滅が目障り：一覧では動かさず、図と要点と詳しい画面に限り、`prefers-reduced-motion` で止める。",
]
