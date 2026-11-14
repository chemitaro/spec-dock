package spec

// 計画（Epic）。型 specdock/v1。
// Epic の計画は、子の Scope への切り分けを持つ。実装の手順とテストは子の Scope が持つ。

goal: "SpecDock のダッシュボードの構造の図、ボード、横の欄の見出しに、Scope に対応する worktree のエージェントの稼働の印を出し、横の欄から Orca で開けるようにする。"

// 子の Scope への切り分け。子の題名は GitHub に、保証レベルは子の requirement.cue にある。
slices: {
	"iss-00591": {
		covers: ["R-01", "R-02", "R-03", "R-04", "F-02", "F-04", "F-05"]
		text: """
			orca-web の場所の設定と、要約の読みと、Scope と worktree の対応（D-01〜D-05）。
			サーバー：`config.json` の `orca_web` の節、Host の名前からのオリジン、画面の CSP、リポジトリの一覧の API の `server.orca_web`、構造の API の worktree の記録。
			画面：`core/orca_match.js`（対応と状態の純粋な計算、node のテスト）と `core/orca.js`（部品の import、1つの読みの輪、試し直し、知らせ）。
			画面に印はまだ描かない。受け入れは、Python のテスト（設定、CSP、API）、node のテスト（対応の計算と状態）、本物の orca-web（127.0.0.1:8791）に対して `core/orca.js` が要約を読み、iss-00589 の worktree が iss-00589 に対応することの確かめ（ブラウザーのコンソールか小さな確かめの式。写しは要らない）。
			この Issue を先に分けるのは、epic-00526 の iss-00593 が同じ対応と状態を使い、iss-00592 の画面の作業を待たずに始められるようにするため。
			"""
	}
	"iss-00592": {
		covers: ["R-05", "R-06", "R-07", "R-08", "R-09", "F-01", "F-03", "F-06"]
		text: """
			構造の図の箱と枠、ボードの札、横の欄の見出しへの稼働の印と、横の欄の「Orca で開く」（D-06、D-07）、配る文書（D-08）。
			受け入れは、node と Python のテストに加えて、本物の orca-web に対する headless Chrome の写し（構造の図とボードと横の欄、1440・1000・390、明るい・暗い）と、orca-web を止めたときの写し（印もボタンもなく、図とボードが動く）、ボタンの iframe の読み込みの回数の測り（R-08）を report.md に残す。
			"""
		after: ["iss-00591"]
	}
}

verification: """
	各 Issue の report.md（仕様のレビュー、コードのレビュー、最終品質ゲートの合格、写し）。
	Epic の確かめ：統括が、本物の orca-web と SpecDock のダッシュボードを 127.0.0.1 と Tailscale の IP の両方で開き、作業中のエージェントのいる Issue の箱・札・横の欄に印が出ること、横の欄から Orca で開けること、orca-web を止めると印が消えて図とボードが動くことを見る。
	"""

rollback: "子の Issue の PR を戻す。`config.json` に `\"orca_web\": {\"enabled\": false}` を書けば、版を戻さずに連携だけを止められる（CSP も今に戻る）。"

exit: "2つの子の Issue が閉じ、SpecDock の版を出して、この PC のダッシュボードで印とボタンが動くことを統括が確かめた。"

execution: {
	sessions: {
		spec: {
			task:      "Epic の要件・設計・計画と切り分け（この文書を書いたセッションの記録）"
			model:     "Opus 5.5"
			effort:    "high"
			rationale: "統括（spec-dock の main の統括役）が Orca の依頼 task_87517b448497 で選んだ。方針の第3節「設計・曖昧な調査・判断」"
		}
		owner: {
			task:      "各 Issue のタスク担当（Issue の仕様、実装担当の起動、レビュー、最終品質ゲート）"
			model:     "Opus 5.5"
			effort:    "medium"
			rationale: "方針の第2節、standard のタスク担当。実装担当のモデルは各 Issue の計画で選ぶ（iss-00591 のサーバーと純粋な計算はテストで確かめられる実装、iss-00592 はフロントエンドの設計と実装）"
		}
	}
}
