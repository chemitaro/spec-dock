package spec

// 計画（Epic）。型 specdock/v1。

goal: "orca-web の要約が指揮の親と開始の時刻を返し、印の並びを指揮の関係で決める。その上に、Epic・Initiative の枠の worktree の印と、押した印のエージェントを開く口を作り、リポジトリの構造の図、次に『横断の構造』で、印から印への指揮の線と『指揮の帯』を出す。"

// この Epic の外の前提（型にない項目）。別のリポジトリの Issue なので、slices の鍵にも、
// SpecDock の依存（GitHub の blocked-by。リポジトリをまたいで登録できず SCOPE_NOT_FOUND）にもできない。
prerequisites: {
	"gh:chemitaro/orca-web#43": {
		title: "orca-web の iss-00043（epic-00004 の子）：要約の各エージェントに指揮の親と開始の時刻を、各 worktree に main を足し、稼働の印の並びを指揮の関係の順にする"
		text: """
			D-01 の形を作る：要約（`GET /api/worktrees/summary`、版は変えない）の `agents[].parent {id, worktreeId}`（親がなければ null、見えなければ `{id: null, worktreeId: null}`）、`agents[].startedAt`、`worktrees[].main`、
			印の要素の `data-agent-id`、部品の `buildMarks`（`web/embed/agent-marks-view.js`）の並びを R-14・D-01 の規則（関係なしを先に新しい順、関係ありを後ろに上流から下流、兄弟は新しい順）に改めること、README の部品の契約、
			テスト（ps の `parentPaneKey`、tabs の `orchestration.parentPaneKey`、解けない親、構造化 Chat の合併の後の id、`startedAt` の出どころと動かないこと、並びの場合分け）。
			並びの変更は、orca-web の部品を読むすべての画面（SpecDock のボード・横の欄の見出し・構造の図、orca-web 自身の画面）に効く。
			本人の順序で、iss-00614 の後に始める。iss-00043 の requirement.cue は、2026-11-17 の時点で保証レベルのほかは空なので、この改訂で直すものはない（この内容は、その Issue の仕様を書くタスク担当が、この Epic の R-14・D-01 から書く）。
			"""
		needed_by: ["iss-00616", "iss-00617", "iss-00621"]
		needed_for: "iss-00616 と iss-00617 は、始める前に iss-00043 が orca-web の main に入っていること（統括の改訂の依頼、2026-11-17）。iss-00621 は待たずに作れる（D-09：`data-agent-id` がなくても `buildMarks` の並びで結ぶ）が、R-14 の並びと `data-agent-id` での対応の実データでの確かめは、iss-00043 の後に行う"
	}
}

slices: {
	"iss-00621": {
		covers: ["R-12", "R-13", "R-14", "R-15", "F-06"]
		text: """
			Epic・Initiative の枠の worktree の印と、押した印のエージェントを開く口（D-08、D-09、D-07）：入れ子の枠の見出しと木の枠の箱の `wtMark`、ボードの札の稼働の印の専用の行、
			`paintOrcaMarks` の描いた並びの記録と `markAgentAt`、横の欄の `openAgent`、構造の図・ボード・横の欄の見出し・『横断の構造』の印の押し、F-06。
			R-14 は、SpecDock の側で並べ替えず `buildMarks` の並びを使うことと、iss-00043 の後の実データの並びの確かめを持つ（並びそのものは iss-00043 が作る）。
			実機の確かめで、作業中の Epic の worktree にエージェントがいる実例（統括が試しの送り先を用意する）を写す。
			依存：iss-00620（印の DOM と専用の行に触れるため）と iss-00614（本人の順序、『横断の構造』の印の押しを同じ Issue で作るため）の後（`iss-00621 → iss-00620`、`iss-00621 → iss-00614`、登録済み）。
			どちらも別の Epic の Issue なので `after` には書かず依存で順序を持つ。
			"""
		session: "owner"
	}
	"iss-00616": {
		covers: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "F-01", "F-02", "F-03", "F-04", "F-05"]
		text: """
			リポジトリの構造の図（D-02〜D-05、D-07、D-10）：純粋な計算 `views/graph/command.js` と node のテスト、印の位置 `markSpots`（iss-00620 の行の規則と同じ詰め）、
			親の印から子の印への線（箱の中の短い線と端の層）、同じ箱・帯の同じ項目の中の親子の弧と `cmdAudit`、枠の見出しの印から枠の中の Issue の箱の印へ降りる線、
			世界の中の指揮の層と『指揮の帯』、点の流れと波紋、減らす設定、指揮の色の札、凡例の行、印（箱・枠・帯）を押したときの線の目立たせと帯のエージェントの詳細の欄のチャット、`収める`、390px。
			iss-00614（epic-00612）が `graph.js` の部品を `draw.js` に取り出した後、iss-00620（epic-00573）が印を専用の行に置いて配置が行の数を知る形にした後、iss-00621 が並びの記録と `openAgent` を作った後、
			orca-web の iss-00043 が main に入った後に始める（依存 `iss-00616 → iss-00614`、`iss-00616 → iss-00620`、`iss-00616 → iss-00621` は登録済み。iss-00043 は `prerequisites`）。
			iss-00614 と iss-00620 は別の Epic の Issue なので `after` には書かず依存で順序を持つ。
			"""
		after: ["iss-00621"]
		session: "owner"
	}
	"iss-00617": {
		covers: ["R-10", "R-11"]
		text: """
			『横断の構造』（D-06、D-07、D-10）：リポジトリごとの対応と居場所、各リポジトリの印の位置と同じ箱の弧、枠ごとの帯と全体の帯「ほかの場所」、`compose` の帯の高さ、R-11 の入れ物の例外、
			リポジトリをまたぐ印から印への線、重なりの順、edgeAudit と `cmdAudit`。
			iss-00616 の計算と部品を使い、iss-00614 の `compose`・`allgraph.js` に足す（依存 `iss-00617 → iss-00616`、`iss-00617 → iss-00614`、登録済み）。
			"""
		after: ["iss-00616"]
		session: "owner"
	}
}

verification: """
	iss-00043（orca-web）：要約の単体テスト（親あり・親なし・見えない親・合併の後の id・main・`startedAt` の出どころと状態が変わっても動かないこと）、`buildMarks` の並びの単体テスト（R-14 の場合）、印の `data-agent-id` のテスト、orca-web の全テストと lint。
	iss-00621：枠の `wtMark` の HTML（doing と branch の有無）、ボードの札の専用の行（エージェントの有無）、`markAgentAt` の node のテスト（`data-agent-id` あり・なし、`+N`、記録の数が違う）、`openAgent` の選びのテスト、構造の図・ボード・横の欄の見出し・『横断の構造』の押しの静的な検査、
	今のテストがそのまま通ること、合成の要約での 1440・390 × 明・暗の写し、作業中の Epic の worktree の実例の写し、`make lint` と全テスト。iss-00043 の後に、実データで並びと押した印の選びを確かめて report.md に残す。
	iss-00616：command.js と `markSpots` の node のテスト（D-02・D-10 の場合）、構造の図の今のテストがそのまま通ること（組がないときの HTML が同じ）、合成の要約と状態の置き場の写しでの 1440・1000・390 × 明・暗の写し、
	edgeAudit の違反0、`cmdAudit` の `boxOverlaps`・`edgeOverlaps` 0、印の位置の検査（`markSpots` と描いた印の差 1px 以内）、ブラウザーのエラー0、減らす設定の写し、`make lint` と全テスト。最後に実データで、線・弧・帯を確かめて report.md に残す。
	iss-00617：compose の帯の高さと R-11 の例外の node のテスト、『横断の構造』の今のテストがそのまま通ること、同じ写しの確かめ、すべてのリポジトリの edgeAudit の違反0と `cmdAudit` 0、全テスト。
	最後に統括がブラウザーで、実際の Orca の親子（統括 → タスク担当 → 実装担当、同じ worktree の親子、作業中の Epic の worktree のエージェント → 枠の中の Issue、別のリポジトリの統括）で、線・弧・帯・波紋・印の並び・押した印のチャットを確かめる。
	"""

rollback: "各 Issue の PR を戻す。iss-00617 を戻すと『横断の構造』の線と帯がなくなり、iss-00616 を戻すとリポジトリの構造の図の線と帯と色の札がなくなり、iss-00621 を戻すと枠の worktree の印とボードの専用の行がなくなり、印を押したときは今どおり前の選びのエージェントが開く。iss-00043 を戻しても、SpecDock は F-01 として線を出さず、印は今の状態の順に戻るだけで壊れない。"

exit: "iss-00043、iss-00621、iss-00616、iss-00617 が閉じ、実際の Orca の親子が、リポジトリの構造の図と『横断の構造』に、親の印から子の印への黄色の動く線と帯で出て、どこの印を押してもそのエージェントのチャットが開く。"

execution: {
	sessions: {
		plan: {task: "Epic の仕様と切り分け（この記録。2026-11-17 の改訂を含む）", model: "Opus 5.5", effort: "high", rationale: "統括が方針の第3節（設計・判断）から選んで起動した値の記録。改訂も同じ値で統括が起動した"}
		owner: {task: "各 Issue のタスク担当（Issue の仕様、実装担当の起動、関門）", model: "Opus 5.5", effort: "medium", rationale: "方針の第2節、standard のタスク担当。実装担当は Issue の計画で選ぶ（iss-00043 はテストで確かめられるサーバー側と部品の並びなので GPT-6.1 Sol / medium、iss-00621 は既存の画面への小さな足しと押しの対応で、node のテストで確かめられるので GPT-6.1 Sol / medium、iss-00616・iss-00617 は見た目と動きと幾何の設計を含むフロントエンドなので Opus 5.5 / medium を推す）"}
	}
}
