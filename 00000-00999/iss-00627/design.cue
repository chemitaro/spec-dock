package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"画面の見出しの寸法を layout.js の寸法の写しにし、ふつうの枠では描いた後に測り直さない（初めの表示を遅くしない）",
	"題名の折り返しのように描くまで分からない寸法だけを、描いた後に測って配置をやり直す（iss-00620 の稼働の印の行と同じ仕組み）",
	"router.js の直しは、今の並べ方が車線を S 未満に残す束でだけ働く後戻りの並べ直しにし、きれいに解けている束の経路は変えない",
]

current: """
	- layout.js：縮めていない枠の見出しは `padT + SIZE.head(46) + grow + (rows − 1) × MARK_ROW`、縮めた枠の高さはそれに `padB` を足した値。pad は Initiative [16,16,16]、Epic・Issue [9,12,12]。
	- graph.css：`.gx-ini` は上の縁 4px・余白 12/16/16、`.gx-epic` は縁 1px・余白 9/12/12。`.gx-fh` の行は字の大きさ × 行の高さ 1.6（Initiative 25.6px、Epic 21.6px）、`.gx-fm` は min-height 18px で中身 19.2px。
	  縮めた Epic の題名は2行まで折り返す（line-height 1.45）。
	- router.js の寄せ：`range()` は範囲が C.WIDE（160px）より広い線分の目指す範囲を A* の位置1点に縮める（wide）。束の並びの比べ `cmp` は、動かない線分との前後を、この縮めた範囲で決める。
	  `lacking()` は wide の線分の不足を申告しない。`assignPorts` は入口にその線だけなら入口を出口の高さにそろえる。
	"""

target: """
	- graph.css の見出しの行は layout の写し（22px と 18px、Epic の上の余白 8px、縮めた枠の下の余白 Epic 11px・Initiative 15px）。
	- layout の options に `heads`（縮めた枠の測った高さ）を足し、縮めた枠の高さは max（今の値, heads）+ grow。
	- graph.js・allgraph.js の `checkRows` は、稼働の印の行と一緒に縮めた枠の中身の実寸を測り、違うときだけ配置をやり直す（合わせて2回まで）。
	- router.js の寄せは、近い組が残る束でだけ、(a) wide を外して並べ直し、(b) 動かない線分を飛び越す並べ方を試す。入口の高さそろえは、向かいの出口とぶつかるときは使わない。
	"""

design: {
	"D-01": {
		title: "見出しの行を layout の寸法に固定する（graph.css）"
		text: """
			次の規則にする（ほかの規則は変えない）。どれも layout.js の `SIZE.head`（22 + 6 + 18）と `SIZE.pad` の写しで、コメントに「layout.js の写し。一緒に直す」と書く。

			```css
			.gx .gx-epic { … padding: 8px 12px 12px; … }          /* 上の縁 1px + 8px = pad の 9 */
			.gx .gx-epic.is-compact { width: 236px; padding-bottom: 11px; }   /* 下の縁 1px + 11px = pad の 12 */
			.gx .gx-ini.is-compact { padding-bottom: 15px; }                  /* 下の縁 1px + 15px = pad の 16 */
			.gx .gx-fh { …; min-height: 22px; … }
			.gx .gx-fh > :is(.gx-kicker, .gx-fttl) { line-height: 22px; }      /* 題名の行 22px */
			.gx .gx-fm { …; height: 18px; line-height: 18px; }                  /* 要約の行 18px */
			```

			Initiative は上の縁 4px + 余白 12px = pad の 16 のまま。行の高さは題名と見出しの字（kicker）にだけ当て、`.gx-agents`（orca-web の部品）には継がせない（MARK_ROW 20 のまま）。
			縮めた Epic の題名の `line-height: 1.45` と2行の折り返しは今のまま（より詳しい規則が勝つ）。docid の札（21.25px）と状態の印（19px）は 22px の行に収まる。
			"""
		satisfies: ["R-01", "R-02"]
	}
	"D-02": {
		title: "縮めた枠の測った高さを layout の入力にする（layout.js）"
		text: """
			```js
			/** A compact frame's height from its rows of agents, before the routing's growth for ports (the CSS of D-01 fits a one-line title in it). */
			export function compactHeight(kind, rows = 1) // pad 上 + SIZE.head + (rows − 1) × MARK_ROW + pad 下
			```

			`layout(scopes, cleanup, options, gaps)` の options に `heads: {Scope id: px}` を足す（縮めた枠の中身の測った高さ、上の縁から下の縁まで、倍率 100%）。
			`frameBlock` の縮めた枠は `base = compactHeight(kind, rows)`、`fit = max(base, heads[id] ?? 0)`、`h = fit + grow`。`fit > base` のときだけ block と flatten の node に `fit` を持たせる（rows と同じく、渡さないときの JSON を変えない）。
			縮めていない枠と箱は `heads` を読まない。routeLayout の折り返しの基準（breaks）の layout にも同じ options を渡す（今のまま）。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "描いた後に縮めた枠を測り、違うときだけ配置をやり直す（graph.js・allgraph.js）"
		text: """
			新しい module `views/graph/measure.js`（DOM を読むのは `compactNeeds` だけ、ほかは純粋）：

			```js
			/** {Scope id: px} — every compact frame's content height at 100% (top edge to bottom edge), or null when it cannot be measured (F-01). */
			export function compactNeeds(root, scale)
			/** Whether a layout's compact frames would take other heights with these needs (or these rows of agents). */
			export function headsDiffer(nodes, needs)
			/** The needs above their frame's compactHeight: what heads keep. */
			export function tallNeeds(nodes, needs)
			```

			`compactNeeds`：root が隠れている・幅0は null。各 `.gx-frame.is-compact` で、`.gx-fm` の computed style が flex でなければ null（graph.css が未適用）。
			高さ = ceil（（`.gx-fm` の下端 − 枠の上端）/ scale + 下の余白 + 下の縁 − 0.25）（測りの小数の誤差で、ちょうど収まる1行の枠が 1px 高く測られないよう、0.25px までの超えは切り捨てる）。
			`headsDiffer`：縮めた frame の node ごとに `max(compactHeight(kind, rows), needs[id] ?? 0)` が `node.fit ?? compactHeight(kind, rows)` と 0.5px より違えば true。

			graph.js：`V.heads` を足し、`buildWorld` の routeLayout に `heads: V.heads` を渡す。`checkRows` は `measureMarks` に続けて `compactNeeds(V.el.world, V.s)` を測り（null なら heads は今のまま）、
			行の数の違い（今の判定）か `headsDiffer` のどちらかで違えば、今と同じ `rowsRedo`（2回まで、F-02）で render をやり直す。`V.heads` は `tallNeeds(nodes, needs)`（compactHeight より高い測りの値だけ）に置き換える（実装で足した：1行の枠だけのときは heads が空のままで、allgraph.js のリポジトリの印が測るたびに変わらない）。
			allgraph.js：リポジトリごとの `r.heads`、`sigOf` に `JSON.stringify(r.heads)`、`layoutRepo` の routeLayout に `heads: r.heads`、`checkRows` は graph.js と同じ判定（リポジトリごとの `rowsRedo`）で、`r.heads` も `tallNeeds` の値。
			"""
		satisfies: ["R-02", "F-01", "F-02"]
	}
	"D-04": {
		title: "寄せの並べ直し（router.js の nudgePass）"
		text: """
			`range()` は、wide で縮める前の目指す範囲を `flo0`・`fhi0` に残す。`nudgePass` の束ごとの並べ方（今の cmp・ord・詰め・中央への寄せ）を、束の中の関数 `arrange()` にまとめ、`{ord, x, over, nb}` を返す。

			1. `res = arrange()`。近い組の数 `close(res)`：nb で重なる2本（範囲の重なり > 0.5px、別の線、どちらかが動く）で、位置の差が S − 0.5 未満のもの。
			2. close > 0 で束に wide の線分があれば、wide を外し（`wide = false`、`dlo0 = flo0`、`dhi0 = fhi0`）、`res = arrange()`。
			3. それでも close > 0 なら、飛び越しの並べ方を作る：res.ord の順に、動く線分ごとに `req = dlo0` から、先の動く線分（nb）の位置 + S と、動かない線分（nb）から S − 0.5 未満の位置を越えるまで req を上げる。
			   ord は位置の順に並べ直す。すべての動く線分が自分の hi 以内で、close が減るときだけ採る。
			4. 採った res で経路を書き、今と同じく `lacking(ord, conf, V, over > 0.5, x, nb)` で不足を申告する。

			close が0の束は 1 の結果だけを使うので、今きれいに解けている束の経路は変わらない（ほかの束の変化が後の回に及ぶことはある：R-05 で比べる）。
			"""
		satisfies: ["R-03", "R-04", "R-05"]
	}
	"D-05": {
		title: "入口の高さそろえ（router.js の assignPorts）"
		text: """
			「まっすぐ届く線」（入口の辺にその線だけで、出口の高さが入口の範囲の内）の規則は、`facing(G, Z, e.y1)`（入口の辺のすぐ左でその高さに向かい合う障害物）が線の出る箱 `e.a` でなく、
			その出口（`exits`）が e.y1 から S − 0.5px 未満にあるときは使わず、入口の格子の位置のままにする。
			"""
		satisfies: ["R-03", "R-04", "R-05"]
	}
	"D-06": {
		title: "回帰の入力（tests/fixtures/issue627/）"
		text: """
			この PC の状態の置き場の写しから、受入の組の routeLayout の入力（構造の API の scopes と cleanup、稼働の印の測った幅、見える幅、範囲）を取り、題名と本文の文字（scopes の title、cleanup の text）を伏せ（title は Scope の ID、text は code）、配置に使わない項目（url、path、reason、pr、branch、worktrees、todos など）を落として固定する。
			依存、親、子、状態、段、推奨の順、番号、日時（active_at・closed_at：活動の順に使う）、keep_visible、merge は残す（配置と経路はこれで決まる。伏せる前と同じ違反の数になることを S-01 で確かめた）。node のテスト（tests/js の検査の口）で routeLayout と audit を走らせ、違反0を確かめる。
			"""
		satisfies: ["R-03"]
	}
	"D-07": {
		title: "実機の確かめ"
		text: """
			隔離した venv（この worktree の wheel）と一時の状態の置き場（この PC の状態の置き場の写し）、別のポートで `dashboard serve --offline --tailscale`、試しの orca の中継（GET だけ、iss-00614 の relay_orca.py の写し）。
			headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で、R-04 の組の edgeAudit（倍率 100%、稼働の印の後）、R-01 の見出しの下端の差、R-02 のはみ出し、
			1440・390 × 明暗の写し（直す前と後、日本語の題名が切れないこと）を report.md に残す。
			"""
		satisfies: ["R-01", "R-02", "R-04"]
	}
}

compatibility: "API・保存・モデルは変わらない。layout の options に heads がなければ、配置の JSON は今と同じ。graph.css の見出しの規則は構造の図と横断の構造の枠だけに当たる。"

risks: [
	"飛び越しの並べ方は交差を減らす並びの順より位置を優先するので、その束では交差が1つ2つ増えることがある（近い組の解消を優先する）",
	"字体の違いで題名の行の中身が 22px を越える環境では、縮めていない枠の見出しが少し下へはみ出しうる（行の高さを px で固定するので、ふつうは起きない）",
]
