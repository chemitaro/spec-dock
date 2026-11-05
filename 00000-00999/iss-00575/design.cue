package spec

design: {
	"D-01": {
		title:     "切れ目の候補ごとに全体の倍率を計算して選ぶ"
		satisfies: ["R-01", "R-02"]
		text:      "layout.js の childrenBlock で、最上位（parent が null）かつ options.height があるとき、まず各ブロック（Initiative、依存でつながったまとまり、折りたたみの塊）を自然な幅で作る。widestRoom が、先頭から k 個の幅の合計（間は wrapCol）を候補の幅とし、shelved で棚に詰めたときの全体の幅と高さを求め、倍率 min(1, 幅/(w+2×margin), 高さ/(h+2×margin)) が最大のものを選ぶ（同じなら面積が小さいほう、それも同じなら先の候補。最上位のすべてのブロックに同じように働く）。選んだ幅を shelfBlock に渡す。見える高さが見える幅以上のときは、今までの幅（avail）を返す。依存でつながったまとまりは一つのブロックなので、切れ目は鎖の中に落ちない。"
	}
	"D-02": {
		title:     "配線の広げ直しでは切れ目を固定する"
		satisfies: ["R-03"]
		text:      "routeLayout が通路を広げるとき（gaps が空でない）は、ctx.breaks（最初の配置の wraps）が各棚の個数を固定するので、候補の計算は行わない。"
	}
	"D-03": {
		title:     "ページは図の領域の実寸を渡し、変わり終わってから並べ直す"
		satisfies: ["R-03"]
		text:      "graph.js の buildWorld が routeLayout に width（view.clientWidth − 16）と height（view.clientHeight − 16）を渡し、V.width と V.height に残す。新しい配置の判定（sig）に両方を入れる。onResize は applyT のあと、200ms 変わらなかったら relayout を呼び、幅も高さも V と同じなら何もしない。"
	}
}
