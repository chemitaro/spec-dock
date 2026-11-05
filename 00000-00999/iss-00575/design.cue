package spec

design: {
	"D-01": {
		title:     "残りの幅に収まる Initiative を、その幅で作り直して並べる"
		satisfies: ["R-01", "R-02"]
		text:      "layout.js の childrenBlock で、最上位（parent が null）のとき、まず Initiative を全体の幅で配置して、左から行に並べる。依存でつながっていない Initiative が行の残りに入らないとき、残りの幅が Initiative の最小幅（420）以上なら、その幅で作り直す。作り直した枠が残りに収まり、高さが「行の下に積んだときの高さ（行の高さ ＋ 行の間 ＋ 全幅での高さ）」以下なら採る。採った幅は wraps の root#shares に残す。依存でつながったまとまり（gridBlock）、Epic などほかの最上位の Scope は今までの幅のまま。その後は既存の shelfBlock が、幅で行を折り返す。"
	}
	"D-02": {
		title:     "採った幅を固定して、配線の広げ直しで動かさない"
		satisfies: ["R-03"]
		text:      "採った幅を layout の wraps に \"root#shares\"（[まとまりの番号, 幅] の並び）として残す。routeLayout が通路を広げるときは、最初の配置の wraps を breaks として渡すので、そこに root#shares があれば作り直しの判断をせずにその値を使う。"
	}
}
