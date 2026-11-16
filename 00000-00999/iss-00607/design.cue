package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"依存の線の範囲を選ぶ値 `deps` を、layout・保存・道具の帯からなくし、今の deps all の計算だけを残す",
	"線・配置の結果は今の deps all とまったく同じにして、見た目とテストの期待を保つ",
]

current: """
	layout.js の DEFAULTS は `{mode, range, deps: "all", focus}`。`pairs` は deps none なら空、deps wait なら終わった依存を飛ばす。
	prefs.js は版3 `{mode, range, deps, legend}` と、版2から mode・deps・legend（showDone から range）、版1から mode・legend を戻す。
	graph.js の道具の帯は 拡大縮小、収める、入れ子/木、見せる範囲、依存の線（待っている線｜すべての線｜線なし）。savePrefs は 4つの鍵を書く。
	"""

target: """
	DEFAULTS は `{mode: "nest", range: "now", focus: null}`。pairs は今の deps all の分かれ道だけを持つ。
	prefs.js は版3 `{mode, range, legend}`。道具の帯は 拡大縮小、収める、入れ子/木、見せる範囲。
	"""

design: {
	"D-01": {
		title: "依存の線（layout.js の pairs と DEFAULTS）"
		text: """
			- DEFAULTS から deps を消す。layout の options の注釈から deps を消す。
			- `pairs` の `if (opts.deps === "none") return [];` と `if (done && opts.deps === "wait") continue;` を消す。ほかの規則（holder のない相手、これからの done の端、親子、木の祖先、組のまとめと done の論理積）は今のまま。
			- 呼ぶ側が options に deps を渡しても、どこでも読まない（`rangeOpts` は `{...DEFAULTS, ...options}` のままでよいが、deps に基づく分かれ道は残さない）。
			- 返す `L.opts` に呼ぶ側の deps が写っても、router.js と graph.js は読まない（router.js は deps を読んでいない。2026-11-16 に確かめた）。
			"""
		satisfies: ["R-02", "F-01"]
	}
	"D-02": {
		title: "保存（prefs.js、graph.js の savePrefs）"
		text: """
			- `PREFS_KEY = "specdock.graph.v3"`、`LEGACY_KEYS` は今のまま。
			- `VALID` から deps を消す。`restorePrefs` の返り値は `{opts: {mode, range}, legend}`。版3は mode・range・legend、版2は mode・legend（range は showDone から）、版1は mode・legend を確かめて戻す。deps はどの版でも読まない。
			- 冒頭の注釈を、版3に deps がない（前の deps は読まずに捨て、次に書くときに消える）ことに直す。
			- graph.js の `savePrefs` は `{mode, range, legend: V.legend}` を書く。`loadPrefs` は今のまま（opts を V.opts に写す）。V.opts に deps は入らない。
			"""
		satisfies: ["R-04", "F-01"]
	}
	"D-03": {
		title: "道具の帯（graph.js）"
		text: """
			- `renderTools` の `<span class="tool-group" role="group" aria-label="依存の線">…</span>` を丸ごと消す。見せる範囲の group で帯が終わる。
			- `onClick` の `else if (a === "deps") o.deps = act.dataset.deps;` を消す。
			- graph.css は変えない（`.tool-group[role="group"]` の規則は見せる範囲の group に今どおり効く。390px では縦の部品が1つ減るので帯が短くなる）。消した group だけのための規則があれば消してよい（今はない）。
			- 凡例（renderLegend）と選んだ箱の強調は変えない。
			"""
		satisfies: ["R-01", "R-03", "R-05"]
	}
	"D-04": {
		title: "テストの書き換え"
		text: """
			- `dashboard_graph_check.mjs` の組み合わせから deps の繰り返しをなくす（wait の組は消し、all の組を deps なしで残す）。
			- `test_dashboard_graph_js.py` の small の wait・all・none の layout と、その線の比べ（T の series、`pairs("wait")` など）は、
			  「deps wait・none を渡しても deps なしと同じ edges」と「終わった依存が is-done で出る」の確かめに書き換える。context の wait も同じ。
			- `test_dashboard_graph_range.py` の deps の繰り返しは、deps なし（今の all と同じ結果）にする。`tests/fixtures/issue603/layout-before.json` の digest のうち deps all の組とだけ比べる（wait の組は使わない。fixture の中身は書き換えない）。
			- restorePrefs のテストは、版3・版2の deps が返り値に出ないことにする。
			- toolbar のテスト：帯に deps の group と3つの文字がないこと（R-01）、押したあとの保存が3つの鍵だけ（R-04）、版3に deps none を保存した状態で描いても edges が deps なしと同じで出る（F-01。harness が edges の数か世界の線の HTML を返せるなら、それで確かめる）。legacy の run の `{"act": "deps"}` のクリックは消す。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "F-01"]
	}
}

compatibility: """
	保存の鍵は v3 のまま。前の deps は読まれず、次に何かを押したときの書き込みで消える。線の切り替えで wait・none を選んでいた人は、すべての線で始まる。
	PR を戻すと、deps のない版3は deps の既定（all）で読まれるので、前の動きに戻る。構造の API とモデルは変わらない。
	"""

risks: [
	"deps の分かれ道を消すときに deps all の計算まで変えると、線と配線の結果が変わる。iss-00603 の digest（deps all の組）と比べて同じことを確かめる",
]
