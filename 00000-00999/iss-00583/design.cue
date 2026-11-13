package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"塊を先に、つながりのない Scope を塊の棚の空きに詰める規則を、childrenBlock の1か所に入れる",
	"配線の広げ直しの仕組み（gap のキー、gapFor、ctx.breaks）を壊さない入れ物の形にする",
	"最上位の折り返しを、ほかの段と同じ規則にそろえる",
]

current: """
	childrenBlock(parent, kids, ctx, avail) は、子を活動順に並べ、components で依存のまとまりに分け、まとまりごとに
	1つなら ctx.node、2つ以上なら gridBlock、全部が畳まれるならチップ（最後）を items に入れ、shelfBlock(key, items, ctx, room, rowBase) で
	左から右へ並べて幅で折り返す。最上位で高さがあれば widestRoom が room を選ぶ。ctx.breaks は、gaps のない配置の各棚の個数で、
	広げ直しの回は棚の切れ目をそれに固定する。
	"""

target: """
	childrenBlock は、items を「塊」（gridBlock の結果）と「1つ」（ctx.node の箱と枠、片付けのチップ）に分け、新しい packBlock に渡す。
	packBlock が、塊の棚、空きへの詰め込み、残りの棚を決める。最上位も同じで、widestRoom と shelved は消す。
	"""

design: {
	"D-01": {
		title:     "並べる順：塊を先に、1つを後に"
		satisfies: ["R-01", "F-03"]
		text: """
			components の結果を今までどおり活動順（各まとまりの最初の Scope の順）に回し、2つ以上で、全部が畳まれないものを groups（gridBlock）に、
			1つのものを singles（ctx.node）に入れる。全部が畳まれるまとまりのチップ（key.f）は singles の最後に足す。
			groups どうし、singles どうしの順は、それぞれ活動順のまま。gridBlock のキー（`${key}~${g}`、g は components の番号）は今までと同じにする。
			"""
	}
	"D-02": {
		title:     "塊の棚"
		satisfies: ["R-01", "R-03", "F-01"]
		text: """
			groups を左から右へ置き、次の塊が見える幅（avail）を超えるところで次の棚にする（今までの shelfBlock と同じ規則。塊は分けない）。
			棚の高さ H は、その棚の塊の高さの最大。塊の間の横の間は wrapCol（14、gap のキーは今までの wc<key>）。
			"""
	}
	"D-03": {
		title:     "空きへの詰め込み（最初に入る場所）"
		satisfies: ["R-01", "F-01", "F-03"]
		text: """
			singles を順に1つずつ、塊の棚を上から順に見て、最初に入る場所に置く。1つの棚の中では、次の順に試す。

			1. 棚の右の列：すでにある右の列（左から順）。列は、先頭の Scope の幅を持つ縦の積み重ねで、最後のものの下（縦の間 wrapRow 14）に、
			   幅が列の幅以下で、下の端が H 以下なら入る。
			2. 新しい右の列：棚の今の右の端 + wrapCol + 幅 ≤ avail で、高さ ≤ H なら、新しい列の先頭になる。
			3. 塊の下：棚の塊を左から順に、塊の下の空き（幅は塊の幅、上の端は塊の下の端 + wrapRow、下の端は H）に、行を左から右へ（横の間 wrapCol）、
			   行が埋まれば次の行（縦の間 wrapRow）で入れる。入るのは、行の右の端が塊の幅以下で、下の端が H 以下のとき。

			どの棚のどこにも入らないものは、塊の棚の下に、今までの shelfBlock と同じ棚（活動順、avail で折り返す）で並べる。塊がない段は、
			すべてがこの棚になるので、直す前と同じ座標になる（F-02）。H は詰めたもので伸ばさない（F-01）。
			"""
	}
	"D-04": {
		title:     "入れ物の形と、広げ直しの回での固定"
		satisfies: ["R-03"]
		text: """
			配線の広げ直し（gapFor、gap、axisOf）が今までどおり働くように、詰めた結果を入れ物の木で表す。

			- 段の全体：縦（axis y）の入れ物 wr<key>（今までと同じ）。子は、塊の棚と残りの棚。
			- 塊の棚：横（axis x）の入れ物 wc<key>（今までと同じ）。子は、左から、塊の置き場と右の列。
			- 塊の置き場：塊の下に何もなければ塊そのもの。あれば縦の入れ物（塊、その下の行…）。下の行は横の入れ物。
			- 右の列：縦の入れ物（先頭、その下…）。
			- 新しい入れ物のキーは、段のキー、棚の番号、置き場の番号を含み、ほかと重ならない。axisOf が、横の入れ物のキーに x、縦の入れ物のキーに y を返すようにする
			  （今の axisOf は wc で始まるキーと c で始まるキーを x とするので、それに合わせて名前を選ぶか、axisOf を直す）。
			- 入れ物の中の間は gap(ctx.gaps, キー, 基準, i) で求め、広げ直しで広がる。

			置き場の決め方（どの Scope が、どの棚の、どの置き場の、どこに入るか）は、gaps のない配置で一度だけ決めて ctx.wraps に残し、
			gaps のある回（ctx.breaks がある回）は、それをそのまま使う（大きさや H が変わっても、置き場を選び直さない）。ctx.wraps の値の形は変えてよい。
			"""
	}
	"D-05": {
		title:     "最上位の折り返し"
		satisfies: ["R-02", "R-03"]
		text: """
			childrenBlock の最上位で widestRoom を呼ぶのをやめ、ほかの段と同じく avail（options.width − 2 × margin、なければ WRAP_WIDTH − 2 × margin）で packBlock に渡す。
			widestRoom と shelved は消す。最上位の棚の間は今までどおり BASE.world、ほかの段は BASE.wrapRow。
			layout の options.height は受け取るが使わない（JSDoc を直す。graph.js は今までどおり渡し、大きさが変わり終わってからの並べ直しの合図に使う）。
			縦長の画面では、avail が狭いので、Initiative は1列に積まれる。
			"""
	}
	"D-06": {
		title:     "テスト"
		satisfies: ["R-01", "R-02", "R-03", "F-01", "F-02", "F-03"]
		text: """
			tests/unit/presentation/test_dashboard_graph_js.py（node の確認 tests/js/dashboard_graph_check.mjs を通す）に、合成の構造を足す。

			- epic-00313 に似せた構造：Epic 1つの中に、つながりのない Issue 5つ（1つは作業中）、2つの鎖（a → b）、6つから1つへ集まる背の高い塊
			  （うち1本は c → d → 集まる先）、4列2行の塊。幅 1000・1440・1920（高さあり）で並べる。
			- 背の高い1つ（棚の高さより高い枠）を持つ Initiative。
			- 塊のない Epic（12の Issue、今の wide の構造で足りる）。

			確かめること：R-01 の受け入れ（棚の範囲、重なりなし、枠の高さが直す前より低い）、F-01（背の高い1つは塊の棚の下）、F-02（塊のない段の座標が直す前と同じ。
			今の test_groups_without_dependencies_wrap_at_the_width_seen がそのまま通る）、R-03（gaps ありで置き場が同じ、edgeAudit 0）。

			改める前の決定に合わせた期待の更新：iss-00575 の test_initiatives_wrap_where_the_whole_shows_largest（倍率の切れ目）は、行が見える幅に収まることを確かめる形に改め、
			test_without_a_height_the_top_level_wraps_at_the_width_seen は高さありでも同じ行になることを確かめる形に改める。
			test_a_chain_of_initiatives_is_one_block_on_one_row は、鎖が1行に残ることを保ち、1つの Initiative の置き場は新しい規則で決まる値にする。
			test_frames_follow_activity_and_boxes_put_done_below の読み順は、塊を先に置く規則で変わる箇所だけを直し、変わる理由をコメントに書く。
			どの期待を、なぜ変えたかは report.md の「逸脱と判断」に書く。
			"""
	}
}

compatibility: "表示の配置だけが変わる。API、データ、URL、保存した設定は変わらない。graph.js が渡す options は同じ。"

risks: [
	"塊の下に詰めた Scope に、ほかの親の Scope からの依存の線が来ると、通り道が塊の近くで混む。広げ直しが gap のキーで広げるので、入れ物の形（D-04）を守れば違反は残らない。edgeAudit のテストで確かめる",
	"塊を先に置くので、作業中の1つの Scope が、活動順の後の塊より右か下に来る。本人の要望（塊を左に）を優先する",
]
