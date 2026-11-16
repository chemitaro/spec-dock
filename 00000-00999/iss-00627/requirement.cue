package spec

// 要件（Issue）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "ダッシュボードの表示だけを直し、データや操作には触れない"
}

purpose: """
	構造の図（各リポジトリの `/r/<repo>/` と『横断の構造』`/graph`）で、依存の線が箱や枠の見出しに重なったり、
	線どうしが車線の間隔（8px）より近く重なったりしないようにする。配置が見込む箱・枠の大きさを画面で描いた実寸と一致させ、
	線の通り道の計算（router.js）が車線の重なりを残したまま『足りている』と判断する不具合を直す。
	"""

background: """
	iss-00614 の実機の写し（report.md の『実機の写し』と『次の提案』）で、倍率 100% の `specdockEdgeAudit` に違反が残った：
	housing-lifecycle『全体』1440 で boxHits 6、taikyohiyou_project『全体』1440 で overlaps 2・1000 で 1、『いま』390 で 8・『全体』390 で 1。
	明暗によらず、各リポジトリ単体の構造の図でも同じ数。

	この Issue の測り（2026-11-17、report.md の『原因』）で、原因は2つに分かれた。

	1. 枠の見出しの実寸が配置の見込みより高い（DOM の側）。layout.js は見出しの行 22px・要約の行 18px（`SIZE.head` 46）と上の余白（Epic 9px）を見込むが、
	   画面では Initiative の題名の行が 25.6px（16px × 行の高さ 1.6）、要約の行が 19.2px、Epic は上の縁 1px が余白に入っていない。
	   見出しの下端は Initiative で +4.8px、Epic で +1.8px ずれ、線がその帯を通ると boxHits になる（housing-lifecycle）。
	   子のない縮めた枠（is-compact）は高さを配置の値で固定するので、中身が下へはみ出す（1行の題名で +1〜2.5px、2行に折り返すと +20px）。
	   edgeAudit は枠の矩形を測るので数えないが、線がはみ出した文字の上を通りうる。
	2. 線の通り道の計算そのもの（node でも再現する）。taikyohiyou_project の overlaps は、DOM ではなく、稼働の印の行で高くなった箱を入れた
	   routeLayout の結果に既にある（稼働の印のない node の audit で 0 だったのは、入力が違ったため）。router.js の寄せ（nudging）に3つの不具合：
	   (a) 範囲の広い線分を A* の位置に留める近道（iss-00578）が、動かない線分の手前に並べられると、車線を重ねたまま、不足も申告しない、
	   (b) 入口の辺に S おきに並んだ動かない線分（櫛）の間に、動く線分が挟まって抜け出せない、
	   (c) 入口にその線だけのとき入口を出口の高さにそろえる規則が、向かいの箱の出口と同じ高さに入口を置く（taikyohiyou を見える幅 1424 で単体にした node の overlaps 1）。

	統括の決定（2026-11-17、msg_61e7c3c8f34f）：見出しは案1（実寸を見込みに合わせる。見出しの行の高さを layout の px に固定し、Epic の上の余白 9→8 で縁を吸収し、
	2行に折り返した縮めた枠だけ描いた後に測り直す）。router の直しもこの Issue に入れ、node の 240 組の比べで悪化0を受入にする。
	木の表示の taikyohiyou『全体』の違反 9 は直す前から同じで、統括が別の Issue にする。
	"""

includes: [
	"`views/graph.css` の枠の見出しの行の高さと余白",
	"`views/graph/layout.js` の縮めた枠の高さ（測った高さを入力に持つ）",
	"`views/graph/router.js` の寄せと入口の高さ",
	"`views/graph.js` と `views/allgraph.js` の、描いた後の縮めた枠の測り直し",
	"テスト（`tests/unit/presentation/`、`tests/unit/infra/`、`tests/js/`、`tests/fixtures/issue627/`）",
	"実機の写し（受入の組、1440・390 × 明暗、日本語の題名）",
]

excludes: [
	"木の表示（mode tree）の線の違反（統括が別の Issue にする）",
	"箱（`.gx-box`）・枠の幅、箱の高さ、配置の並び方（段・行・折り返し）、layout.js の `SIZE` の値",
	"構造の API、モデル、orca-web の部品",
	"線を描いた後に違反を隠す直し（検査の余白を変える、測る要素を変えるなど）",
]

requirements: {
	"R-01": {
		title: "入れ子の枠の見出しの実寸が、配置の見込みと一致する"
		text: """
			縮めていない枠（Initiative・Epic・子のある Issue）の見出し（`.gx-fh` と要約の行 `.gx-fm`）の下端が、layout の見込みの見出しの中身の下端
			（枠の上端 + pad の上 + `SIZE.head` + (rows − 1) × MARK_ROW。線の口の伸び grow を除く）と一致する。grow は線の口のために見出しの障害物だけを高くする分で、DOM の中身には入らないので、grow のある枠では中身の下端が `headY2` より上にある。
			題名の行は 22px、要約の行は 18px に固定し、Epic の上の余白を 8px にして上の縁 1px を吸収する。Initiative の題名 16px は行の高さ 22px で、上下が切れない。
			"""
		acceptance: [
			"実機（1440・390、明暗）で、すべての縮めていない枠の `.gx-fm` の下端と、見込みの見出しの中身の下端（grow を除く）の差が 0.5px 以内で、`headY2` を 0.5px より越える枠が0（測りの道具の写しを report.md に残す）",
			"`graph.css` に題名の行 22px・要約の行 18px・Epic の上の余白 8px の規則がある（静的な検査）",
			"日本語の題名（Initiative・Epic）が上下で切れないことを、1440・390、明暗の写しで確かめて report.md に残す",
		]
	}
	"R-02": {
		title: "縮めた枠の中身が枠の外へはみ出さない"
		text: """
			子のない縮めた枠の高さは、題名が1行のとき今の配置の値のまま（中身がちょうど収まるよう、下の余白を Epic 11px・Initiative 15px にする）。
			題名が2行に折り返した枠は、描いた後に中身の実寸を測り、配置の見込みより高ければ、その高さで配置をやり直す（iss-00620 の稼働の印の行と同じく、知らせ1回・描画1回につき2回まで）。
			"""
		acceptance: [
			"layout に縮めた枠の測った高さ（`heads`）を渡すと、その枠の高さが max（今の高さ, 測った高さ）+ 線の口の伸びになり、渡さなければ今の layout と同じ JSON",
			"実機（1440・390、明暗）で、縮めた枠に scrollHeight が clientHeight を越えるもの（中身のはみ出し）が0",
		]
	}
	"R-03": {
		title: "線の通り道の計算が、車線の重なりを残したまま終わらない"
		text: """
			router.js の寄せで、(a) 範囲の広い線分を A* の位置に留めた並べ方が、重なる2本を S − 0.5px より近く残すときは、その束を広い線分も目指す範囲の全体で並べ直す。
			(b) それでも近い2本が残るときは、動く線分を、動かない線分から S 以上離れた高さ（位置）へ飛ばして並べ直し、範囲の内に収まり、近い組が減るときだけ採る。
			(c) 入口にその線だけのとき入口を出口の高さにそろえる規則は、入口の辺のすぐ左で向かい合う障害物（線の出る箱でない）が、その高さから S − 0.5px 未満に出口を持つときは使わない。
			"""
		acceptance: [
			"iss-00627 の固定した入力（taikyohiyou_project『いま』360・『全体』360・872・1312・1424、housing-lifecycle『全体』1344。題名を伏せた構造と稼働の印の幅）で、node の routeLayout の audit の違反（boxHits・ownHits・overlaps・diagonal・portShare・trunkOverlaps・failed）が0",
			"(c) の向かい合う出口の小さな入力で、入口が向かいの出口と S − 0.5px 未満にならない",
			"既存の構造の図のテスト（代表の構造・context・packing の audit の違反0）が通る",
		]
	}
	"R-04": {
		title: "受入の組で、画面の線の検査の違反が0"
		text: """
			この PC の状態の置き場の写し（`dashboard serve --offline`）で、倍率 100%、稼働の印が出てから、次の組の `window.specdockEdgeAudit()` の違反（boxHits・ownHits・overlaps・diagonal・portShare・failed・missing・markOverflow）がすべて0。
			各リポジトリ単体の構造の図：housing-lifecycle『全体』（窓 1440）、taikyohiyou_project『全体』（窓 1440・1000・390）・『いま』（窓 390、見える幅 360）。
			『横断の構造』（`/graph`）：1440・1000・390 × 『これから・いま・全体』。いずれも明・暗。
			"""
		acceptance: [
			"上の組のすべてで違反0（数を report.md の表に残す）",
		]
	}
	"R-05": {
		title: "ほかの構造の線を悪くしない"
		text: "この PC の 9 つの登録のうち Scope のある 8 つのリポジトリの構造 × 入れ子（範囲3 × 見える幅 344・360・600・872・984・1240・1312・1344・1424）・木（範囲3 × 1240）の 240 組（8 × 30）で、直す前と後の node の audit を比べ、違反の数が増える組が0。"
		acceptance: [
			"240 組の比べの結果（増えた組0、減った組、変わらない組、経路が同じ組）を report.md に残す",
		]
	}
}

failures: {
	"F-01": {
		title: "測れないときは、測り直さず今の配置のまま"
		text:  "構造の図が隠れている、幅が0、graph.css がまだ当たっていない（要約の行が flex でない）ときは、縮めた枠を測らず、`heads` を変えない。"
	}
	"F-02": {
		title: "測り直しは、知らせ1回・描画1回につき2回まで"
		text:  "稼働の印の行の測り直し（iss-00620 F-03）と同じ数え（`rowsRedo`）を使い、縮めた枠の高さと行の数のどちらで違っても、合わせて2回まで配置をやり直す。"
	}
}

constraints: [
	"線を描いた後に違反を隠す直し方はしない（統括の決定）。`edgeAudit` と router の `audit` の検査の規則は変えない",
	"layout.js の `SIZE`（箱の大きさ、`head: 46`）は変えない（`test_the_box_size_does_not_change`）",
]

decisions: [
	"見出しは案1（統括 msg_61e7c3c8f34f）：実寸を見込みに合わせる。題名の行 22px、要約の行 18px、Epic の上の余白 8px、2行の縮めた枠だけ測り直す",
	"router の直しもこの Issue に入れ、node の 240 組で悪化0を受入にする（同上）",
	"木の表示の taikyohiyou『全体』の 9 は、次の提案に書く（同上）",
	"router の回帰の入力は、この PC の実データから題名・本文を伏せて固定する（公開リポジトリに題名を載せない）",
]
