package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"見せる範囲を1つの値 `range`（all・now・next）にし、layout・保存・道具の帯がこの1つだけを見る",
	"全体・いまは今の2つの組（showDone・fold）とまったく同じ結果にして、今の見え方とテストの期待を保つ",
]

current: """
	layout.js の DEFAULTS は `{mode, showDone, deps, fold, focus}`。`visibility` は showDone か、開いていれば出し、
	`showsDone(p)` は showDone・focus・開いていて候補 a でない親で真。`folds` は fold かつ候補かつ keep_visible でないもの。
	木では fold を偽にする。`pairs` は線の切り替えで終わった依存を出すかを決める。
	prefs.js は版2（`specdock.graph.v2`、`{mode, showDone, deps, fold, legend}`）と、版1から mode・fold・legend を戻す。
	graph.js の道具の帯は 拡大縮小、全体（fit）、入れ子/木、終わったものも、線の切り替え、片付けの候補を畳む（入れ子だけ）。
	"""

target: """
	DEFAULTS は `{mode: "nest", range: "now", deps: "all", focus: null}`。layout は range から、内部の showDone・fold・next を導く。
	prefs.js は版3（`{mode, range, deps, legend}`）と、版2・版1からの移し替え。道具の帯は 拡大縮小、収める、入れ子/木、見せる範囲（3つ）、線の切り替え。
	"""

design: {
	"D-01": {
		title: "layout の範囲の正規化（layout.js）"
		text: """
			`layout(scopes, cleanup, options, gaps)` の options は `{mode, range, deps, focus, width, height}`。range が "all"・"now"・"next" でなければ "now"。
			冒頭で範囲を内部の値に直す：

			| range | showDone | fold | next |
			|---|---|---|---|
			| all | true | false | false |
			| now | false | 入れ子なら true（木は false） | false |
			| next | false | false | true |

			返す `L.opts` には range と、導いた showDone・fold・next を入れる（routeLayout と graph.js が読む）。
			呼ぶ側から showDone・fold を渡しても使わない（range だけが入力）。全体・いまの残りの計算（visibility、showsDone、folds、childrenBlock、tree、pairs）は今のまま。
			"""
		satisfies: ["R-01", "R-02", "R-03"]
	}
	"D-02": {
		title: "これからの見せる判定（layout.js の visibility）"
		text: """
			next のとき、`visibility` を次の規則にする（memo と循環の扱いは今のまま）：

			- `hidden(s)` = `s.state === "done"` または `cleanup` に s の id がある（コードの種類 a・b・c を問わない）。
			- `visible(s)` = `!hidden(s)` または、子のどれかが `visible`。
			- focus は今のとおり `s.id === focus` で必ず出る（R-06）。focus の下の Scope は上の規則に従う。

			これで、a（開いた子孫がない）は消え、b・c は候補でない開いた子孫を持つときだけ枠として出る。
			next の `showsDone(p)` は常に偽（focus も）。段は `stage.open` で数える（終わったものは出ないため）。
			fold は偽なので畳んだ塊は作られない。
			"""
		satisfies: ["R-04", "R-06"]
	}
	"D-03": {
		title: "これからの依存の線（layout.js の pairs）"
		text:  "next のとき、`blocked_by` の相手 `src` か、待つ側 `s` のどちらかが state done なら、その組を飛ばす。線の切り替え none は今のとおり空、wait・all はこの規則の上で今のまま。見えない Scope は今のとおり holder がないので線にならない。"
		satisfies: ["R-05"]
	}
	"D-04": {
		title: "保存の版3と移し替え（prefs.js）"
		text: """
			- `PREFS_KEY = "specdock.graph.v3"`、`LEGACY_KEYS = ["specdock.graph.v2", "specdock.graph.v1"]`（新しい順）。
			- `restorePrefs(current, legacies, defaults)`：current は版3の値、legacies は `[版2の値, 版1の値]`（読めないものは null）。
			  返り値は `{opts: {mode, range, deps}, legend}`。
			- 版3（記録の形のとき）：mode・range・deps・legend を確かめて戻す。
			- 版3がなく版2が記録：mode・deps・legend を確かめて戻し、range は `showDone === true` なら "all"、それ以外は "now"。fold は使わない。
			- 版3・版2がなく版1が記録：mode・legend だけ（今の版1→版2 と同じく showDone・deps を戻さない。fold は使わない）。
			- 確かめ：mode は nest・tree、range は all・now・next、deps は all・wait・none、legend は真偽値。誤りは項目ごとに既定。
			graph.js の `loadPrefs` は 版3 と LEGACY_KEYS の値を読んで渡し、`savePrefs` は `{mode, range, deps, legend}` を PREFS_KEY に書く。
			"""
		satisfies: ["R-07", "F-02"]
	}
	"D-05": {
		title: "道具の帯（graph.js、graph.css）"
		text: """
			- `tool("done", …)` と `tool("fold", …)` を消し、入れ子/木のボタンのすぐ後に
			  `<span class="tool-group" role="group" aria-label="見せる範囲">` の3つのボタン（`data-act="range" data-range="all|now|next"`、aria-pressed、icon と `.lab`）を置く。入れ子と木の両方で出す。
			- title：全体＝「見せる範囲：全体（終わったものも、片付けの候補も出す）」、いま＝「見せる範囲：いま（開いている親の中の終わったものを灰色で出し、片付けの候補は畳む）」、
			  これから＝「見せる範囲：これから（着手できる・作業中・止められている・不明だけを出す）」。
			- `onClick` の `done`・`fold` を `range`（`o.range = act.dataset.range`）に置き換え、保存して描き直す。
			- fit：見える文字「収める」、title・aria-label「画面に収める」。動きは変えない。
			- 390px：今の `.tool-group[role="group"]` の CSS（縦に並べ、文字を隠して icon だけ）がそのまま効く。足すのは要るときだけで、新しい色を使わない。
			"""
		satisfies: ["R-01", "R-08", "R-09"]
	}
	"D-06": {
		title: "片付けの候補の印と凡例（graph.js）"
		text: """
			- `boxHtml`：range が all で、Scope が片付けの候補なら、`.gx-marks` に枠と同じ `<span class="cln" title="片付けの候補：…" role="img" aria-label="片付けの候補">box</span>` を足す（箱と木の枠の箱の両方）。
			- `frameHtml`：next のときは印を出さない（全体・いまは今のまま）。
			- 凡例の「片付けの候補」を「片付けの候補（全体では箱と枠に印、いまでは畳んで1つに、これからでは出さない）」にする（長いので `wide`）。
			"""
		satisfies: ["R-02", "R-08"]
	}
	"D-07": {
		title: "これからで何も出ないときの知らせ（graph.js）"
		text: """
			buildWorld の後、range が next で layout の nodes が0なら、図の場所に「これから進める Scope はありません。全体で、終わったものを見られます。」を出す（道具の帯と札の帯は残す）。
			`showEmpty` は帯を隠すので使わず、図の中の別の要素（既存の部品の文字の色 `--ds-muted`）にする。範囲を変えると消える。
			選択とパネルは今のまま（選んだ Scope が見えなくなっても、今の showDone を外したときと同じ）。
			"""
		satisfies: ["F-01", "F-03"]
	}
}

compatibility: """
	保存は版3になる。版2の showDone が真の人は「全体」、それ以外は「いま」で始まり、mode・deps・凡例は引き継がれる。版2の fold を偽にしていた人は「いま」（畳む）に戻る（本人の決定どおり）。
	古い鍵は消さないので、PR を戻すと版2の値で前の見え方に戻る。構造の API とモデルは変わらない。
	"""

risks: [
	"全体・いまの座標が変わると、既存の配置のテストと実データの見え方が崩れる。D-01 で今の組と同じ計算にし、テストで今の組と比べる",
	"これからで枠だけが残る b・c の親の配置が、配線の広げ直し（routeLayout）で違反を出す。dashboard_graph_check.mjs の組み合わせに next を足し、edgeAudit の違反0を確かめる",
]
