package spec

// 設計（Issue）。型 specdock/v1。

goals: ["『これから』の特別扱いを、指揮の線・行・帯の計算から取り除き、範囲の違いを Scope の箱と枠の見せ方（routeLayout）だけにする"]

current: """
	`range === "next"` の分岐が4か所にある（iss-00668 D-02・D-04・D-05・D-06）。
	- `views/graph.js` の `paintCommand`：`drawn = range === "next" ? [] : all`（線の組を空にする）。
	- `views/allgraph/command.js` の `crossPlace`：`for (const pair of next ? [] : pairs)`、`next` のときの `early`・`commanding` による keep、`if (!next)` の『ほかの場所』の行。
	- `views/graph/unscoped.js` の `unscopedItems`：`range === "next"` のときだけ `count`・`countParts` を付け、Unlinked を `count` のあるものに絞り、印なしの項目を落とす。`childCount`・`countTitle`・`commanding` はそのためだけにある。
	- `views/graph/command.js` の `countWidth`、`views/graph/command_view.js` の `.gx-band-count` の札、`views/graph.css` の `.gx-band-count`。
	"""

target: "どの範囲でも、線の組・居場所・行の項目・帯は同じ計算で決まる。range は routeLayout（箱と枠）と、描き直しの鍵（commandKey・crossKey）にだけ入る。"

design: {
	"D-01": {
		title: "構造の図の paintCommand は、どの範囲でも全部の組を置く"
		text: """
			`views/graph.js` の `paintCommand` で `drawn` をやめ、`commandPairs(summary)` の全部を `placeAgents` に渡す。`unscopedItems` には `range` を渡さない（引数ごとなくす）。
			居場所は今の `placeAgents`（`placer`）のまま：見える箱の印、畳んだ塊の縁、`routeLayout` の『これから』で隠れた Scope はいちばん近い見える祖先の枠、どれもなければ帯（epic-00615 R-02）。
			描き直しの鍵 `commandKey` の `range` は残す（範囲で箱が変わり、居場所が変わるため）。
			"""
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title: "crossPlace の next の分岐を取り除き、keep を iss-00617 R-03 の規則にする"
		text: """
			`views/allgraph/command.js` の `crossPlace` から `next` を取り除く：組はどの範囲でも置き（F-02 の unknown のときの見送りは今のまま）、keep は今の全体・いまの規則（見せていないリポジトリの帯に組の親の端があるとき）だけ、『ほかの場所』の行はどの範囲でも作る。
			`range` の引数は受けても使わない形にせず、取り除く（呼び手の allgraph.js も渡さない）。`crossKey` の `range` は残す。
			`bandShape`・`crossModel`・F-05 の組み直しの上限（`A.shapeRedo < 2`）は変えない。
			"""
		satisfies: ["R-01", "R-03", "F-02"]
	}
	"D-03": {
		title: "unscopedItems から range と子の数を取り除く"
		text: """
			`views/graph/unscoped.js` の `unscopedItems` から `range` の引数、`count`・`countParts` の計算、『これから』の絞り込みを取り除く。項目は今の全体・いまの出し方（Primary、Unlinked の全部と薄い項目と `+N`、線の端の印なしの項目）。
			使われなくなる `childCount`・`countTitle`・`commanding`、`blank` の `count`・`countParts`、`UNSCOPED.count`、`views/graph/command.js` の `countWidth`（`itemWidth` の数の足し）、`views/graph/command_view.js` の `.gx-band-count` の札、`views/graph.css` の `.gx-band-count` の規則を消す（`.gx-band-badge` は残す）。
			"""
		satisfies: ["R-02"]
	}
	"D-04": {
		title: "テストを『これから』の線に合わせ、退行を防ぐ合成の入力を足す"
		text: """
			node（`tests/js/` と `tests/unit/presentation/` の pytest の包み）：
			- `crossPlace` に実データの形の合成の入力（3つのリポジトリ、main の統括 → 別のリポジトリの worktree の子、同じ worktree の親子、Unscoped の行、`range` の違い）を通し、『これから』の可視の集合でも組が全部残り、居場所が帯・印・枠に決まる。
			- 構造の図の居場所：『これから』の routeLayout で隠れた Scope の worktree の子の端が、いちばん近い見える祖先の枠になる。
			画面（偽の DOM と偽の orca）：構造の図と『横断の構造』の『これから』で `.gx-cmd` に線があり、specdockCmdAudit の links・arcs が『いま』と同じ組の入力で 0 より多く、子の数の札がない。
			iss-00668 のテストのうち『これから』で線がない・数が付く・指揮していない Unlinked が出ない・枠の keep が commanding で決まる、を確かめるものは、この決定に合わせて直し、直したテストの名前を report.md に列挙する。全体・いまのテストは変えずに通す。
			"""
		satisfies: ["R-04", "R-01", "R-02", "R-03"]
	}
	"D-05": {
		title: "実機の確かめ"
		text: """
			`uv build --wheel` の wheel を一時の venv に入れ、一時の状態の置き場（この PC の状態の置き場の写し）と別のポートで `spec-dock dashboard serve` を立てる。orca-web は常駐の要約を、CDP の Fetch の中継で別のポートの Origin に許して読む（常駐のダッシュボードと orca-web は止めない・設定を変えない）。
			`/graph` と `/r/<repo>/` の『これから』『いま』『全体』の specdockCmdAudit・specdockEdgeAudit を数え、1440・390 × 明・暗の写しを report.md に残す。
			"""
		satisfies: ["R-04"]
	}
}

compatibility: "画面だけの変更。保存・API・既定の見方は変わらない。子の数の札がなくなり、『これから』に線と、指揮していない Unlinked の項目が出る（移行の案内に書く）。"

risks: [
	"『これから』で隠れた Scope の線が祖先の枠に集まり、枠の縁が混む：iss-00668 の前の 0.9.8 までの見え方と同じで、実機の写しで確かめる",
]
