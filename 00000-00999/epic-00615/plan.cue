package spec

// 計画（Epic）。型 specdock/v1。

goal: "orca-web の要約が指揮の親を返し、その上に、リポジトリの構造の図、次に『横断の構造』で、指揮の線と『指揮の帯』を出す。"

// この Epic の外の前提（型にない項目）。別のリポジトリの Issue なので、slices の鍵にも、
// SpecDock の依存（GitHub の blocked-by。リポジトリをまたいで登録できず SCOPE_NOT_FOUND）にもできない。
prerequisites: {
	"gh:chemitaro/orca-web#43": {
		title: "orca-web の iss-00043（epic-00004 の子）：要約の各エージェントに指揮の親を、各 worktree に main を足す"
		text: """
			D-01 の形を作る：要約（`GET /api/worktrees/summary`、版は変えない）の `agents[].parent {id, worktreeId}`（親がなければ null、見えなければ `{id: null, worktreeId: null}`）と `worktrees[].main`、
			印の要素の `data-agent-id`、README の部品の契約、テスト（ps の `parentPaneKey`、tabs の `orchestration.parentPaneKey`、解けない親、構造化 Chat の合併の後の id）。
			本人の順序で、iss-00614 の後に始める。
			"""
		needed_by: ["iss-00616", "iss-00617"]
		needed_for: "実データでの確かめ（D-07）。合成の要約での実装とテストは、この前提を待たずに進めてよい"
	}
}

slices: {
	"iss-00616": {
		covers: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "F-01", "F-02", "F-03", "F-04"]
		text: """
			リポジトリの構造の図（D-02〜D-05、D-07）：純粋な計算 `views/graph/command.js` と node のテスト、世界の中の指揮の層と『指揮の帯』、点の流れと波紋、減らす設定、指揮の色の札、凡例の行、帯のエージェントの選びと詳細の欄のチャット、`収める`、390px。
			合成の要約で作り、最後に iss-00043 の後の実データで確かめる。
			iss-00614（epic-00612）が `graph.js` の部品を `draw.js` に取り出した後の形に足すので、その後に始める（依存 `iss-00616 → iss-00614`、登録済み）。
			iss-00614 は別の Epic の Issue なので、`after` には書かず依存で順序を持つ。orca-web の iss-00043 は `prerequisites` に書く。
			"""
		session: "owner"
	}
	"iss-00617": {
		covers: ["R-10", "R-11"]
		text: """
			『横断の構造』（D-06、D-07）：リポジトリごとの対応と居場所、枠ごとの帯と全体の帯「ほかの場所」、`compose` の帯の高さ、R-11 の入れ物の例外、リポジトリをまたぐ線、重なりの順、edgeAudit。
			iss-00616 の計算と部品を使い、iss-00614 の `compose`・`allgraph.js` に足す（依存 `iss-00617 → iss-00616`、`iss-00617 → iss-00614`、登録済み）。
			"""
		after: ["iss-00616"]
		session: "owner"
	}
}

verification: """
	iss-00043（orca-web）：要約の単体テスト（親あり・親なし・見えない親・合併の後の id・main）、印の `data-agent-id` のテスト、orca-web の全テストと lint。
	iss-00616：command.js の node のテスト（D-02 の場合）、構造の図の今のテストがそのまま通ること（組がないときの HTML が同じ）、合成の要約と状態の置き場の写しでの 1440・1000・390 × 明・暗の写し、edgeAudit の違反0、ブラウザーのエラー0、減らす設定の写し、`make lint` と全テスト。最後に iss-00043 の後の実データで、線と帯を確かめて report.md に残す。
	iss-00617：compose の帯の高さと R-11 の例外の node のテスト、『横断の構造』の今のテストがそのまま通ること、同じ写しの確かめ、すべてのリポジトリの edgeAudit の違反0、全テスト。
	最後に統括がブラウザーで、実際の Orca の親子（統括 → タスク担当 → 実装担当、別のリポジトリの統括）で、線・帯・波紋・選び・チャットの欄を確かめる。
	"""

rollback: "各 Issue の PR を戻す。iss-00617 を戻すと『横断の構造』の線と帯がなくなり、iss-00616 を戻すとリポジトリの構造の図の線と帯と色の札がなくなる。iss-00043 を戻しても、SpecDock は F-01 として線を出さないだけで壊れない。"

exit: "iss-00043、iss-00616、iss-00617 が閉じ、実際の Orca の親子が、リポジトリの構造の図と『横断の構造』に、黄色の動く線と帯で出る。"

execution: {
	sessions: {
		plan: {task: "Epic の仕様と切り分け（この記録）", model: "Opus 5.5", effort: "high", rationale: "統括が方針の第3節（設計・判断）から選んで起動した値の記録"}
		owner: {task: "各 Issue のタスク担当（Issue の仕様、実装担当の起動、関門）", model: "Opus 5.5", effort: "medium", rationale: "方針の第2節、standard のタスク担当。実装担当は Issue の計画で選ぶ（iss-00043 はテストで確かめられるサーバー側なので GPT-6.1 Sol / medium、iss-00616・iss-00617 は見た目と動きの設計を含むフロントエンドなので Opus 5.5 / medium を推す）"}
	}
}
