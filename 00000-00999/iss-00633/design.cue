package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"木の表示の長い通り道で、寄せが、同時に重なる本数に近い車線で線を分ける",
	"広げの繰り返しが、検査の違反を残した巡を違反0として採らない",
	"入れ子の表示の束の並べ方と経路は変えない（詰め直しは木だけ。落ち着きの判定は、違反0の巡では今と同じ）",
]

current: """
	- router.js の `nudgePass`：束ごとに `arrange()`（並びの順 ord を決め、手前から `x(t) + S` より奥に詰め、余りの半分だけ中央へ寄せる）。並びの順は、重なる組（nb）のすべてに、
	  `cmp`（動かない線分との側、交差の数 `crossCount`、同じなら A* の位置と線の番号）で前後を決めた順（閉路は位置で切る）。詰めは「nb の手前の線分のどれか + S」より奥なので、
	  前後の鎖の長さだけ奥へ積む（同時に重なる本数ではない）。近い組が残る束だけ iss-00627 D-04 の (a)・(b) を試す。`lacking()` は、混んだ束（over > 0.5）では、手前の鎖を数え直して不足を申告する（同じ階段の数え方）。
	- layout.js の `routeLayout`：巡ごとに layout → graphInput → route → portRoom。`settled = 広げの要求なし && 出入りの不足なし` なら、その巡を採って終える（problems は 0 とする）。
	  そうでなければ problems（audit の違反の数）を数え、少ない巡を best にし、広げて次の巡へ（最大 10）。
	- 木の表示（graphInput の `nested: false`）では、x の広げはすべて `tree.indent`（全部の段の字下げ）に写る。
	"""

target: """
	- router.js：木の表示で over > 0.5 の束は、`packFree()` の詰め直しを試し、あふれが小さく近い組が増えなければ採る。採った束の不足は置いた位置の超えから申告する。
	- layout.js：落ち着いた巡は、広げの要求・出入りの不足がなく、かつ audit の違反0の巡だけ。problems はどの巡でも数える。
	"""

design: {
	"D-01": {
		title: "木の表示の束の詰め直し（router.js の nudgePass と packFree）"
		text: """
			新しい関数（module の中、export しない）：

			```js
			// 交差の数で前後が決まる2本の向き（A を手前に置くべきなら -1、奥なら 1、決まらなければ 0）。
			// 動く線分と動かない線分は、arrange の cmp と同じく、動く線分が入れる側（片方だけなら）。動かない線分どうしは 0
			function prefer(A, B)
			// 束 gr を、前後の決まる組の順だけを守って、空いた最初の位置に詰める。{ord, x, over, nb, packed: true} を返す
			function packFree(gr, nb, conf)
			```

			prefer：動く線分 m と動かない線分 f は、`before = m.dlo0 + S <= f.pos + 0.5`、`after = f.pos + S <= m.dhi0 + 0.5` が違えば before の側、同じなら 0。
			動く2本は `crossCount(A, B)` と `crossCount(B, A)` が違えば少ないほうの並び、同じなら 0（どちらに置いても交差は同じ）。

			packFree：
			1. nb の組ごとに prefer が 0 でなければ、手前 → 奥の辺を持つ（有向の無閉路のグラフ。閉路が残るときは、入次数0の候補がなければ残りの全部を候補にする）。
			2. 動かない線分の位置は pos。入次数0の候補から、範囲の始まり `a`、`pos`、線の番号の小さい順に1本ずつ取り出す（範囲の始まりの順に詰めると、前後の決まりがなければ同時に重なる本数の車線で足りる）。
			3. 動く線分 sg：`req = max(dlo0, 置いた手前の線分の位置 + S)`。`free(from)` は、from と「置いた nb の線分の位置 + S（from より奥）」を小さい順に見て、置いた nb の線分のどれとも S − 0.5 以上離れた最初の値。
			   `v = free(req)`。v が dhi0 + 0.5 を越え、req が dlo0 より奥なら、`free(dlo0)` も見て、小さいほうを採る（前後の決まりを守ると範囲からあふれるときは捨てる。交差が増えても重ならないほうを採る）。over は `max(v − dhi0)`。
			4. ord は位置の順（同じなら線の番号）。arrange と同じ中央への寄せ（余りの半分だけ奥へ、奥から順に、重なる奥の線分 − S と lo〜hi を守る）をかける。
			   中央への寄せは arrange と packFree の共通の関数 `centre(ord, x, conf)` にする（arrange の今の文をそのまま移す。wide の扱いも同じ）。

			nudgePass の束ごとの処理で、iss-00627 D-04 の (b) の後に：

			```js
			if (!G.nested && res.over > 0.5) {
			  const alt = packFree(gr, res.nb, conf);
			  if (alt.over < res.over - 0.5 && closePairs(alt) <= close) { res = alt; close = closePairs(alt); }
			}
			```

			lacking は引数 `packed` を足し（`lacking(ord, conf, V, over > 0.5, x, nb, res.packed)`）、packed で混んだ束は、手前の鎖を数え直さず、動く線分ごとに `ask(sg, x(sg) − sg.dhi0)` で申告する（近い組の申告は今と同じ）。
			入れ子の表示（`G.nested`）では packFree を呼ばず、res.packed はないので、並べ方・経路・不足の申告は今と同じ。
			"""
		satisfies: ["R-01", "R-03", "R-04", "F-01"]
	}
	"D-02": {
		title: "落ち着いた巡は、検査の違反0の巡だけ（layout.js の routeLayout）"
		text: """
			```js
			const round = { …, problems: problems(G, res) };
			const settled = !res.widen.length && !Object.keys(add).length && !round.problems;
			```

			settled なら、今と同じくその巡を採って終える。そうでなく、広げの要求も出入りの不足もない巡（足す間がない）は、今の `if (!Object.keys(add).length) break;` で、best（違反の最も少ない巡、同じなら早いもの）を採って終える。
			入れ子の表示で今落ち着く巡は違反0なので、採る巡は今と同じ。problems を数える audit は落ち着いた巡でも1回走る（巡ごとに1回）。
			"""
		satisfies: ["R-02", "R-03", "F-02"]
	}
	"D-03": {
		title: "回帰のテスト"
		text: """
			- node の検査の口 `tests/js/dashboard_graph_route_fix.mjs`（iss-00627）の case に、任意の `mode`（既定 "nest"）と `marks: false`（稼働の印を渡さない）を足し、結果に routeLayout の `problems` を返す。
			- `tests/unit/presentation/test_dashboard_graph_tree_route.py`（新しい）：
			  T-01 固定した入力の product・business の木の『全体』（稼働の印なし）で audit の違反0、problems が audit の違反の数と一致。
			  T-02 D-01 の受入の小さな入力（左に `lane: "v"` の親の線、右に 40 個の箱の列、箱 i → i + 5、`nested: false`）を route(G) に渡し、overlaps 0、広げの要求の最大が S 以下。
			  T-03 静的な検査：router.js の packFree の呼び出しが `!G.nested` の条件の中にあり、layout.js の settled が problems を含む。
			"""
		satisfies: ["R-01", "R-02", "R-03"]
	}
	"D-04": {
		title: "比べと実機の確かめ"
		text: """
			- 比べ：直す前（開始のコミットの dashboard の資産の写し）と後で、iss-00627 R-05 の 240 組と固定した入力の 60 組の routeLayout（稼働の印なし）の audit の違反の数と経路の digest を比べる（`.workbench/iss-00633/tools/sweep.py`）。木は、固定した入力 × 範囲3 で稼働の印ありも比べる。
			- 実機：隔離した venv（この worktree の wheel）、この PC の状態の置き場の写し、別のポートで `dashboard serve --offline --tailscale`。headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）、倍率 100%、
			  taikyohiyou_project の木の『全体』（1440、明暗）の `specdockEdgeAudit()` と写し。直す前は開始のコミットの wheel で同じ組を写す。
			"""
		satisfies: ["R-03", "R-04", "R-05"]
	}
}

compatibility: "API・保存・モデルは変わらない。入れ子の表示の配置と経路は変わらない。木の表示では、混んだ束の線の位置と、広げの間（字下げ・行の間）の量が変わりうる。"

risks: [
	"packFree は交差の数が同じ組の前後を決めないので、その束では交差の数が今と違うことがある（重ならないことを優先する。前後の決まる組の順は、範囲に収まる限り守る）",
	"木の大きな構造では、繰り返しが早く落ち着くことが多いが、構造によっては 10 巡で落ち着かず、最も違反の少ない巡になる（今と同じ扱い）",
]
