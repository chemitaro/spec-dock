package spec

design: {
	"D-01": {
		title:     "経路探索の時間を CPU 時間の最小で測る"
		text:      "`tests/js/dashboard_graph_check.mjs` の `check()` が、時間を見る「generated」の focus なしの組み合わせだけ 3 回経路を探し、`process.cpuUsage()` の差（user+system）の最小を `ms` として返す。ほかの組み合わせは 1 回。node の呼び出しの上限時間は、負荷でも切れないよう 1800 秒にする。"
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title:     "bootstrap の timeout のテストの余裕"
		text:      "timeout を 1.0 秒、hook の sleep を 2 秒、止まった後の確認の待ちを 1.5 秒にする。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title:     "印の SVG と配り方"
		text:      "`assets/dashboard/favicon.svg`（accent の角丸の四角に白い S。上の帯の印と同じ）を置き、`index.html` の `<link rel=\"icon\" type=\"image/svg+xml\" href=\"/assets/favicon.svg\">` で指す。`dashboard_http._get` が `/favicon.ico` を同じ SVG で返す。"
		satisfies: ["R-03"]
	}
	"D-04": {
		title:     "Scope が 0 件の札"
		text:      "`views/overview.js` の `repoCard` で、`scopes` が空のとき、本体に `sd-ov__none`（「Scope はまだありません」）を出す。"
		satisfies: ["R-04"]
	}
	"D-05": {
		title:     "文書の目次の背景の上書き"
		text:      "`dashboard_http` が文書の HTML（CUE、Markdown、失敗のページ）の `</head>` の前に、`@media screen and (min-width: 1180px)` で `.ds-layout` に目次の幅の背景と縁の線を敷く `<style>` を足す。"
		satisfies: ["R-05"]
	}
	"D-06": {
		title:     "狭い幅の図の領域を帯の下から始める"
		text:      "`views/graph.css` の `@container app (max-width: 640px)` で、`.gx` の背景を図と同じにし、`.gx-view` の `top` を帯の高さ（46px）にして上に縁の線を引く。"
		satisfies: ["R-06"]
	}
}
