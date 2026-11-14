package spec

// 計画（Epic）。型 specdock/v1。
// Epic の計画は、子の Scope への切り分けを持つ。実装の手順とテストは子の Scope が持つ。

goal: "横の欄と詳しい画面の「エージェント」のタブで、その Scope の worktree のエージェントを選び、orca-web の詳細とチャットを使えるようにする。SpecDock は相手の選びだけを受け持ち、書き込みに関わらない。"

// 子の Scope への切り分け。子の題名は GitHub に、保証レベルは子の requirement.cue にある。
slices: {
	"iss-00593": {
		covers: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "F-01", "F-02", "F-03", "F-04", "F-05", "F-06", "F-07"]
		text: """
			エージェントのタブ（D-01〜D-07）：出す条件、一覧と選び、iframe、描き直しで残すことと Scope を変えたら外すこと、理由の知らせ、書き込みに関わらないことの確かめ、配る文書。
			1つの Issue にまとめるのは、タブを出す条件、選び、iframe の残し方、理由の知らせが、同じ1つの「相手を正しく選ぶ」の判断で、分けると受け入れを別々に確かめられないため。
			前提：epic-00471 の iss-00591（`ctx.orca`、構造の API の worktree の記録）と、epic-00573 の iss-00589（文書のタブを詰める。残りの高さの使い方と、枠と帯の形。2026-11-14 に完了、PR #590）が終わってから始める（GitHub の依存に登録済み）。iss-00592 とは並べて進められるが、どちらも `views/_shared/panel.js` を変えるので、後に入る方が前の変更に合わせる。
			受け入れは、node のテスト（`agents_logic.js` の出す条件と選び、iframe の HTML の文字列）、Python の静的なテスト（D-06）、本物の orca-web（127.0.0.1:8791）に対する headless Chrome の写し（横の欄と詳しい画面、1440・1000・390、明るい・暗い）、orca-web を止めたときと埋め込みのときの写し、Scope を変えたときとエージェントが消えたときに iframe が外れることの確かめ、送信の間のネットワークの記録（D-06）、60 秒の描き直しで本文が残ることの確かめ（R-07）。送信の確かめの宛先は、確かめ専用のものだけにする。orca-web の試しの送り先 `send-test` は orca-web のリポジトリの worktree で、どの SpecDock の Scope にも対応せずタブに出ないので使えない。代わりに、タスク担当が spec-dock のリポジトリに、iss-00593 を名指すブランチ（`<接頭>/iss-00593-send-test`。`branch_names_scope` で iss-00593 に当たる）の確かめ専用の worktree を作り、Orca でそこに作業を任せていない新しいエージェント（Claude Code の空のセッションなど）を置いて、それにだけ害のない短い本文を送る。業務中のエージェント（実装担当、統括、ほかの worker）には送らない。
			常駐の orca-web の `sendEnabled` は、統括の了承を得てから確かめの間だけ true にし、確かめた後に前の値へ戻し、戻したことを画面の送る欄が止まることで確かめる。確かめ専用の worktree とエージェントは、確かめの後に片付ける（worktree を消すのは、タスク担当がその worktree の名前を計画に書いて行う）。
			"""
	}
}

verification: """
	iss-00593 の report.md（仕様のレビュー〈strict なので 2人〉、コードのレビュー、最終品質ゲート〈strict なので 2人〉の合格、写し、ネットワークの記録）。
	Epic の確かめ：統括が、本物の orca-web と SpecDock のダッシュボードを 127.0.0.1 と Tailscale の IP（スマホを含む）で開き、エージェントのいる Issue の横の欄と詳しい画面にタブが出ること、1人ならすぐにチャットが出ること、Scope を変えると前のチャットが消えること、orca-web を止めると理由が出ることを見る。送信は iss-00593 の確かめ専用の宛先だけで確かめる。
	"""

rollback: "iss-00593 の PR を戻す。版を戻さずに止めるときは、`config.json` に `\"orca_web\": {\"enabled\": false}` を書く（タブも印も消え、orca-web に何も要求しない）。送信だけを止めるときは、orca-web の設定の `sendEnabled` を false にする。"

exit: "iss-00593 が閉じ、SpecDock の版を出して、この PC のダッシュボードでエージェントのタブとチャットが動くことを統括が確かめた。"

execution: {
	sessions: {
		spec: {
			task:      "Epic の要件・設計・計画と切り分け（この文書を書いたセッションの記録）"
			model:     "Opus 5.5"
			effort:    "high"
			rationale: "統括（spec-dock の main の統括役）が Orca の依頼 task_87517b448497 で選んだ。方針の第3節「設計・曖昧な調査・判断」"
		}
		owner: {
			task:      "iss-00593 のタスク担当（Issue の仕様、実装担当の起動、レビュー、最終品質ゲート）"
			model:     "Opus 5.5"
			effort:    "high"
			rationale: "方針の第2節、strict のタスク担当。実装担当はフロントエンドの設計と実装（strict は Opus 5.5 / high）を Issue の計画で選ぶ"
		}
	}
}
