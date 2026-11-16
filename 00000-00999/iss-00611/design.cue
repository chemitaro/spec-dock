package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"これからの見せる判定を「子を持つなら、見える子があるときだけ」にし、案A を親の段にまで広げる",
	"全体・いまは1文字も変えず、iss-00603 の digest の比較で確かめる",
]

current: """
	layout.js の `visibility` は、next のとき
	`v = (s.state !== "done" && !cleanup.has(s.id)) || ix.kids.get(s.id).some(visible)`。
	自身が開いていて候補でなければ、子が見えなくても出る（init-00002 の形）。focus は `layout` の `visible` で `s.id === focus` なら必ず出る。
	"""

target: """
	next のとき `v = kids.length ? kids.some(visible) : (s.state !== "done" && !cleanup.has(s.id))`（kids は `ix.kids.get(s.id)`）。
	全体・いまの分岐と focus の扱いは今のまま。
	"""

design: {
	"D-01": {
		title: "これからの見せる判定（layout.js の visibility の next の分岐）"
		text: """
			next のときだけ、`visible(s)` を次にする：

			- 子がある（`ix.kids.get(s.id).length > 0`。状態によらない）：子のどれかが `visible` なら出す。自身の状態と片付けの候補かどうかは見ない。
			- 子がない：`s.state !== "done"` かつ `cleanup` に s の id がないなら出す（今と同じ）。

			`visible` は今のとおり memo を使った再帰なので、下の段から決まる（R-01 の段ごと）。循環の `seen` も今のまま（F-02）。
			`ix.kids` は自分を親とする参照を除くので、自分自身を子に数えない。
			focus は `layout` の `visible = inFocus(s) && (s.id === focus || visibleBase(s))` のまま（R-04）。focus の下の Scope は `visibleBase` に従う。
			全体・いまの分岐（`opts.showDone || s.state !== "done" || … || context(s)`）、showsDone、folds、pairs、stage の数え方は変えない（R-05）。
			枠の中身は `visibleKids` で決まり、出た親には見える子が必ずあるので、中のない枠はこれからでは focus のときだけになる。
			コメントに iss-00611 と規則を1行で書く。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-02"]
	}
	"D-02": {
		title: "テストの合成の構造と期待（test_dashboard_graph_range.py）"
		text: """
			iss-00603 の `_next()` と `SHOWN`・`FOCUS` は変えずに残し（R-03 の2つ目）、この Issue の形を持つ別の合成の構造 `_parents()` を足す（`node`・`closed`・`snapshot`・`document` を使い、片付けの候補はモデルが判定する）：

			| 番号 | 形 | これから |
			|---|---|---|
			| 70 Initiative（開）→ 71・73 Epic（開、それぞれ閉じた Issue 72・74 だけ＝候補 a） | init-00002 の形 | 70・71・73 とも出ない |
			| 80 Initiative（開）→ 81 Epic（開）→ 82 Epic（開）→ 閉じた Issue 83 | 3段（82 が a） | 80・81・82 とも出ない |
			| 90 Initiative（開、子なし）、91 Epic（開、子なし） | 切り分け前 | 出る |
			| 95 Initiative（開）→ 96 Epic（開、閉じた Issue 97 だけ＝a）と 98 Issue（開） | 候補でない子あり | 95 は枠、98 は出る、96 は出ない |
			| 110 Issue（開）→ 111 Issue（開）→ 閉じた Issue 112 | 子を持つ Issue（111 は候補でない。子が終わったものだけ） | 110・111 とも出ない |

			番号の Scope の id は実際の document から取る（Initiative の接頭辞は support の `_PREFIX`）。モデルの片付けの候補がちょうど 71・73・82・96（どれも `all_descendants_closed`）で、70・80・81・95・110・111 が候補でないことも確かめる（前提の確認。2026-11-16 にタスク担当が今のモデルで確かめた。モデルは Issue を候補にしないので、111 は「自身は開いて候補でないが、子が終わったものだけ」の形になる）。
			確かめ（入れ子・木）：これからの nodes の id の集合が期待どおり、95 の type が枠（入れ子 frame、木 tframe）、groups が空。
			同じ構造の全体・いまでは 70・71・73・80・81・82・110・111 が出る（R-05 の2つ目）。
			focus：70 で nodes が {70}、95 で {95, 98}、80 で {80}（R-04）。
			配線：同じ構造で next（入れ子・木、focus）を含む組み合わせの audit の違反0（R-06 の1つ目）。今の `nxt` の fixture と同じ `_run` の `checks: ["layout", "audit"]` を使う。
			R-05 の1つ目は、今の `test_all_and_now_lay_out_as_the_two_old_combinations` がそのまま通ることで確かめる（期待の digest は変えない）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06"]
	}
	"D-03": {
		title: "これからで何も出なくなったときの知らせ（テストだけ）"
		text: """
			graph.js は変えない。今の知らせは layout の nodes が0のときに出るので、親が消えて空になった場合にも出るはず。
			`test_dashboard_graph_toolbar.py` の仕組みで、開いた Initiative とその子の候補 a の Epic だけ（ほかは終わったもの）の構造をこれからで描き、知らせの文が出て、帯が残ることを確かめる。
			"""
		satisfies: ["F-01"]
	}
	"D-04": {
		title: "実データの直す前と後（タスク担当）"
		text: """
			この PC の状態の置き場を `.workbench/iss-00611/state` に写し、直す前（開始のコミット）と後の wheel を別々の隔離した venv に入れ、
			`spec-dock dashboard serve --offline --tailscale --state-root <絶対の道>` を別のポート（前 18611、後 18612。使われていれば別の空きポート）で立てる。
			headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で、orca-web・spec-dock・housing-lifecycle のこれからを 1440・390 × 明・暗で写し、edgeAudit とブラウザーのエラーを数える。
			orca-web の init-00002 が前は出て後は出ないことを、DOM の `data-id` で確かめて report.md に書く。常駐のダッシュボード（47800）と道具の環境には触れない。後の serve は本人の確かめまで残す。
			"""
		satisfies: ["R-06"]
	}
}

compatibility: """
	保存（`specdock.graph.v3`）、API、モデルは変わらない。これからで出る Scope が減るだけ。PR を戻すと元の見え方に戻る。
	"""

risks: [
	"子を持つが子がすべて focus の外にある、のような形はない（子は親の下なので focus の内外は親と同じか、親が focus のとき）。focus 自身は別の規則で出る",
	"これからで、作業中の子を持たない作業中の親（in_progress の Epic で子が候補だけ）も消える。統括の決定 1 どおり（中に見える仕事がない）",
]
