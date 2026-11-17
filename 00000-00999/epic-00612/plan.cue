package spec

// 計画（Epic）。型 specdock/v1。

goal: "一覧の API が入れ子を返し、その上に『横断の構造』の画面を作って、すべてのリポジトリの仕事をチェックアウトの入れ子のまま1枚で見渡せるようにする。"

slices: {
	"iss-00613": {
		covers: ["R-01", "R-02", "R-03", "F-02", "F-03"]
		text: """
			サーバーの側（D-01、D-02）：入れ子を決める純粋な関数、`DashboardSite` の一覧での覚え、`GET /api/v1/repositories` の `parent`（iss-00613 で `tier` も足したが、iss-00635 でなくした）、契約の文書。
			Python の単体テスト（合成の道で、この PC の登録の形、名前の頭だけが同じ隣、途中が2段、隠した親、ambiguous、リポジトリの分からない行）と、HTTP の応答に道が現れないことのテストで確かめる。
			画面は変えない。これだけで、一覧の API の利用者（画面、Orca など）が入れ子を読めるようになる。
			"""
		session: "owner"
	}
	"iss-00614": {
		covers: ["R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "F-01", "F-04"]
		text: """
			画面の側（D-03〜D-07）：`/graph` の道とタブ、`graph.js` からの描画の部品の取り出し、リポジトリの枠の組み立て（compose.js）、`allgraph.js` の読み込み・更新・見せる範囲・横の欄・稼働の印・収める、線の検査、実データでの写し。
			`next` の各リポジトリの中の見え方は iss-00611 の規則に従うので、その後に始める。入れ子は iss-00613 の `parent` を読むので、その後に始める。
			iss-00611 は別の Epic（epic-00573）の Issue なので、`after` には書かず、依存（`spec-dock dependency add --from iss-00614 --to iss-00611`、登録済み）で順序を持つ。
			"""
		after: ["iss-00613"]
		session: "owner"
	}
}

verification: """
	iss-00613：単体テストと HTTP のテスト（`uv run pytest tests/unit/application`）、`make lint`、全テスト。
	iss-00614：組み立ての node のテスト、`graph.js` の振る舞いのテストがそのまま通り、ソースの文字列のテストは調べる場所だけを draw.js に移して同じ中身で通ること（requirement.cue の constraints の2つ目）、実データ（この PC の状態の置き場の写し）の 1440・1000・390 × 明・暗 × 3つの範囲の写しと edgeAudit の違反0、ブラウザーのエラー0を report.md に残す。
	最後に統括がブラウザーで、company-os の入れ子、spec-dock と orca-web が外にあること、『これから』の既定を確かめる。
	"""

rollback: "各 Issue の PR を戻す。iss-00614 を戻すと `/graph` とタブがなくなり、iss-00613 を戻すと一覧の API の `parent` がなくなる（`tier` は iss-00635 でなくした）。保存（`specdock.allgraph.v1`）は残っても害がない。"

exit: "2つの子の Issue が閉じ、`/graph` で、この PC の9つのリポジトリが company-os の入れ子のまま1枚に描かれ、既定の『これから』で見えるものだけが出る。"

execution: {
	sessions: {
		plan: {task: "Epic の仕様と切り分け（この記録）", model: "Opus 5.5", effort: "high", rationale: "統括が方針の第3節（設計・判断）から選んで起動した値の記録"}
		owner: {task: "各 Issue のタスク担当（Issue の仕様、実装担当の起動、関門）", model: "Opus 5.5", effort: "medium", rationale: "方針の第2節、standard のタスク担当。実装担当は Issue の計画で選ぶ（iss-00613 はテストで確かめられるサーバー側なので GPT-6.1 Sol / medium、iss-00614 はフロントエンドの設計と実装なので Opus 5.5 / medium を推す）"}
	}
}
