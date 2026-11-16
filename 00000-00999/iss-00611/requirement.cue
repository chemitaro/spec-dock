package spec

// 要件（Issue）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "ダッシュボードの表示だけを変え、データや操作には触れない"
}

purpose: """
	構造の図の「これから」で、中に進める仕事がない親（Initiative・Epic、または子を持つ Issue）を出さない。
	「これから」を、これから着手・切り分け・続ける仕事だけの見え方にする。
	"""

background: """
	iss-00603 の「これから」は、終わったものと片付けの候補（a・b・c）を出さず、それを持つ親は開いたものの枠としてだけ出す（案A）。
	ただし、自身が開いていて片付けの候補でない親は、中に見えるものがなくても出る。
	本人（2026-11-16）の指摘：orca-web の構造の図の「これから」で、Initiative init-00002 が中のない枠として1つ残る。
	統括が確かめた実データ（常駐の 0.9.4 の構造の API）では、init-00002（ready、子 3）の開いた子は epic-00004 と epic-00016（どちらも ready、片付けの候補 all_descendants_closed）だけで、
	ほかの Scope は終わっている。これからでは2つの Epic が消え、init-00002 だけが中のない形で出る。
	iss-00603 の report でも、spec-dock の init-00468 が同じ形で出ることを観察し、提案に挙げていた。
	"""

includes: [
	"`views/graph/layout.js` の、これからの見せる判定（visibility）",
	"テスト（`tests/unit/presentation/test_dashboard_graph_range.py` の合成の構造と期待、必要なら `tests/unit/presentation/test_dashboard_graph_toolbar.py`）",
	"実データ（orca-web、spec-dock、housing-lifecycle）でのこれからの直す前と後の写しと edgeAudit",
]

excludes: [
	"「全体」「いま」の見え方（見せる Scope、座標、畳んだ塊、線）",
	"状態の札の帯（止められている・着手できる・作業中…の数）",
	"構造の API とモデル（`dashboard_model.py` の片付けの候補の判定）",
	"道具の帯、凡例、ボタンの title、これからで何も出ないときの知らせの文",
	"配布の手引き（`spec-dock/docs/migration.md`）とリリースノート（次のリリースの Issue で書く）",
]

requirements: {
	"R-01": {
		title: "これからでは、子を持つ Scope は、これからで見える子孫が1つ以上あるときだけ出る"
		text: """
			子を持つ Scope（Initiative・Epic、または子を持つ Issue）は、自身の状態や片付けの候補かどうかによらず、これからで見える子が1つ以上あるときだけ出す。
			子がすべて、終わったもの・片付けの候補（a・b・c）か、それだけを持つ親なら、その Scope も出さない。
			これを段ごとに下から決める（Epic が消えれば、その Initiative も消えうる）。
			"""
		acceptance: [
			"開いた Initiative の子が、片付けの候補 a の Epic だけのとき（orca-web の init-00002 の形）、これからの layout の nodes にその Initiative も Epic もない（入れ子・木）",
			"開いた Initiative → 開いた Epic（候補でない）→ 候補 a の Epic の3段で、これからの layout の nodes に3つのどれもない（下から消える）",
			"開いた Issue の子が候補 a の Issue だけのとき、これからの layout の nodes にその親の Issue もない",
		]
	}
	"R-02": {
		title: "これからでは、子を1つも持たない開いた Scope は今どおり出る"
		text:  "まだ切り分けていない Initiative・Epic や、子のない Issue は、終わっておらず片付けの候補でもなければ、今どおり出す。これから切り分けたり始めたりする仕事だから。"
		acceptance: [
			"子のない開いた Initiative と、子のない開いた Epic が、これからの layout の nodes にある（入れ子・木）",
		]
	}
	"R-03": {
		title: "これからでは、候補でない開いた子孫を持つ親は、今どおり枠として出る"
		text:  "子の一部が候補でも、候補でない開いた子孫（着手できる・作業中・止められている・不明）が1つでもあれば、親は今どおり枠として出す。閉じた親 b が、候補でない開いた子孫の枠として出る扱い（iss-00603 の案A）も今のまま。"
		acceptance: [
			"開いた Initiative の子が、候補 a の Epic と開いた Issue のとき、これからの layout で Initiative は枠として出て、開いた Issue は出て、候補 a の Epic は出ない",
			"iss-00603 の合成の構造（`_next()`）のこれからで、今と同じ Scope が出る（`SHOWN` が変わらない）",
		]
	}
	"R-04": {
		title: "URL の focus で絞った Scope 自身は、これからでも今どおり出る"
		text:  "focus の Scope は、子が見えなくても出す（子のない箱か、中のない枠）。focus の下の Scope は R-01〜R-03 の規則に従う。"
		acceptance: [
			"見える子孫のない、子を持つ開いた Initiative に focus したこれからの layout で、nodes がその Initiative だけ",
			"見える子孫のある開いた Initiative に focus したこれからの layout で、その Initiative と、R-01〜R-03 で見える子孫だけが出る",
		]
	}
	"R-05": {
		title: "「全体」「いま」の見え方は変わらない"
		acceptance: [
			"iss-00603 で記録した直す前の digest（`tests/fixtures/issue603/layout-before.json`）と、全体・いまの layout が今どおり一致する",
			"R-01 の形の構造でも、全体・いまの layout ではその Initiative と Epic が出る",
		]
	}
	"R-06": {
		title: "これからの配線に違反がなく、実データで確かめられる"
		acceptance: [
			"合成の構造（R-01〜R-04 の形を含む）のこれから（入れ子・木、focus）のすべての組み合わせで edgeAudit の違反が0",
			"orca-web、spec-dock、housing-lifecycle の実データで、これからの直す前と後を 1440 と 390、明と暗で写し、edgeAudit の違反0とブラウザーのエラー0が report.md にあり、orca-web のこれからで init-00002 が直す前は出て、後は出ないことが示されている",
		]
	}
}

failures: {
	"F-01": {
		title: "これからで出すものが1つもなくなったときは、今の知らせ（iss-00603 の F-01）が出る"
		text:  "親が消えた結果、図が空になっても、道具の帯と札の帯は残り、図の場所に今の知らせ「これから進める Scope はありません。全体で、終わったものを見られます。」が出る。"
	}
	"F-02": {
		title: "親の循環や壊れた親の参照があっても、これからの判定が止まらず、ブラウザーのエラーが出ない"
		text:  "visibility の memo と循環の扱い（今の `seen`）を保つ。"
	}
}

constraints: [
	"layout.js は DOM のない純粋な計算のまま（node のテストで確かめる）",
	"変えるのは range が next のときの判定だけ。all・now の分岐、showsDone、folds、pairs は変えない",
	"新しい色・字体・文言を足さない",
]

decisions: [
	"2026-11-16 本人の指摘：orca-web の構造の図で『これから』を選ぶと Initiative init-00002 が1つ残る。中の Epic は片付けの候補だけで、Initiative は閉じていないので残っている。「中が削除対象（片付けの候補）だけなら、これから行うタスクはないので、これからでは表示しないべき」。",
	"2026-11-16 統括（依頼書）：これからでは、子を持つ Scope は、これからで見える子孫が1つ以上あるときだけ出す。子孫がすべて終わったもの・片付けの候補なら親も出さない。段ごとに下から決める。子を持たない開いた Scope は今どおり出す。候補でない開いた子孫があれば親は今どおり枠として出す。focus の Scope 自身は今どおり出す。全体・いま・状態の札の帯の数は変えない。",
	"iss-00603 の案A との関係：案A は、終わったもの・片付けの候補（a・b・c）を、その下に候補でない Scope があるときだけ枠として出すとした。この Issue は、同じ「中に見えるものがあるときだけ枠として出す」を、自身が開いていて候補でない親（Initiative・Epic・子を持つ Issue）にまで広げたもの。子のない Scope の扱い（終わっておらず候補でなければ出す）は案A のまま。",
	"2026-11-16 タスク担当：「子を持つ」は、状態によらず子が1つ以上あること（終わった子だけでも子を持つ）。終わった子だけを持つ開いた親は片付けの候補 a なので、今もこれからで出ない（結果は同じ）。",
]
