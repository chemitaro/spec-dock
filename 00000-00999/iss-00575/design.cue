package spec

design: {
	"D-01": {
		title:     "最上位の列数を選ぶ"
		satisfies: ["R-01", "R-02"]
		text:      "layout.js の childrenBlock で、最上位（parent が null）のとき、列数 n を 1 から min(Initiative の数, 幅に入る最大の数, 6) まで試す。各 n で、つながっていない Initiative だけを、幅 (avail − (n−1)×列の間) ÷ n で配置し（Epic などほかの最上位の Scope は今までの幅）、既存の shelfBlock に渡す。全体の高さが最小の n を選び、同じなら大きい n を選ぶ（横に並べる）。最上位に Initiative がなければ探索しない。選ぶたびに最後に選んだ n で配置し直すので、wraps は選んだ配置のものになる。依存でつながったまとまり（gridBlock）は、今までの幅で配置する。"
	}
	"D-02": {
		title:     "列数を固定して、配線の広げ直しで動かさない"
		satisfies: ["R-03"]
		text:      "選んだ n を layout の wraps に \"root#cols\" として残す。routeLayout が通路を広げるときは、最初の配置の wraps を breaks として渡すので、そこに n があれば探索せずにその値を使う。"
	}
}
