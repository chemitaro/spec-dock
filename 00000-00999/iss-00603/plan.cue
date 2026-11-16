package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の見せる範囲を「全体｜いま｜これから」の1つの切り替えにする（layout.js・prefs.js・graph.js・graph.css とテスト）"

steps: {
	"S-01": {title: "layout の range（all・now・next）の正規化とこれからの見せる判定・依存の線のテストを書き、直す前のコードで落ちることを確かめる（Red）。今の showDone・fold を渡すテストと dashboard_graph_check.mjs の組み合わせを range に書き換える（全体＝showDone 真・fold 偽、いま＝既定。今の『いまで fold 偽』の組は全体か木に置き換え、意図を保つ）", realizes: ["R-02", "R-03", "R-04", "R-05", "R-06"], status: "todo", session: "impl-sol"}
	"S-02": {title: "layout.js に D-01〜D-03 を実装し、全体・いまが今の組と同じ結果、これからが規則どおり、すべての組み合わせ（next を含む）で edgeAudit の違反0を通す（Green）", realizes: ["R-02", "R-03", "R-04", "R-05", "R-06"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "prefs.js を版3にし（D-04）、版3・版2・版1・壊れた値の移し替えのテストを先に書いてから実装する。graph.js の loadPrefs・savePrefs を新しい形に合わせる（保存の鍵の文字は prefs.js だけ）", realizes: ["R-07", "F-02"], status: "todo", after: ["S-02"], session: "impl-sol"}
	"S-04": {title: "graph.js の道具の帯（D-05）、片付けの候補の印と凡例（D-06）、これからの知らせ（D-07）を実装し、graph.css を要るときだけ直す。帯・印・凡例・知らせの HTML を確かめるテストを足す", realizes: ["R-01", "R-02", "R-08", "R-09", "F-01", "F-03"], status: "todo", after: ["S-03"], session: "impl-ui"}
	"S-05": {title: "make lint と全体の pytest を通す（重い Mac では統括と相談のうえ CI の provider-ci を test lane の証拠にする）", realizes: ["R-01", "R-09"], status: "todo", after: ["S-04"], session: "impl-ui"}
	"S-06": {title: "spec-dock と housing-lifecycle の実データで、3つの範囲を 1440・390、明暗で写し、edgeAudit の違反0を report.md に残し、tailnet の試しの URL を立てる", realizes: ["R-09"], status: "todo", after: ["S-05"], session: "owner"}
}

tests: {
	"T-01": {title: "代表の構造と合成の構造で、range all の layout（入れ子・木）が直す前の {showDone: true, fold: false} と同じ nodes・groups・座標", verifies: ["R-02"]}
	"T-02": {title: "range now と range なしの layout（入れ子・木）が直す前の既定 {showDone: false, fold: true} と同じ nodes・groups・座標", verifies: ["R-03"]}
	"T-03": {title: "合成の構造（a・b（候補でない開いた子孫あり／候補だけ）・c（黄）・開いた親の中の終わった Issue）で、range next の nodes に done の箱と候補の箱がなく、a と候補だけの b は出ず、候補でない子孫を持つ b は枠、groups は空（入れ子・木）", verifies: ["R-04"]}
	"T-04": {title: "range next の edges の pairs に done の Scope がない（deps all・wait）。deps none は空", verifies: ["R-05"]}
	"T-05": {title: "done の Scope と候補の Scope に focus した range next で、focus 自身が出て、その中の done・候補が出ない", verifies: ["R-06"]}
	"T-06": {title: "restorePrefs：版3の正しい値・誤った値、版2の showDone 真・偽・誤り、版1だけ、どれもなし、壊れた値で、期待の opts・legend を返す。graph.js に版1・版2の鍵の文字がない", verifies: ["R-07", "F-02"]}
	"T-07": {title: "dashboard_graph_check.mjs の組み合わせに range next（入れ子・木、幅 1400・374 ほか、focus）を足し、すべてで edgeAudit の違反0", verifies: ["R-04", "R-05", "R-09"]}
	"T-08": {title: "graph.js の描画（node の DOM なしの確かめか文字の検査）で、帯に done・fold のボタンがなく、role=group aria-label『見せる範囲』の3つのボタンと title、fit の『収める』『画面に収める』、凡例の新しい文、全体の箱の .cln、next の知らせの文がある", verifies: ["R-01", "R-08", "F-01"]}
	"T-09": {title: "graph.css の差分に新しい色の値がない（レビューで確かめる）", verifies: ["R-09"]}
	"T-10": {title: "実データ（spec-dock、housing-lifecycle）の3つの範囲 × 1440・390 × 明暗の写しと edgeAudit の違反0、ブラウザーのエラー0が report.md にある。これからで選んだ箱が消えてもエラーが出ない", verifies: ["R-09", "F-03"]}
}

verification: """
	節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py`。最後に `make lint`、`uv run pytest`（全体）。
	実データ：この PC の状態の置き場を `.workbench/iss-00603/state` に写し、隔離した venv（作業ツリーの wheel）で
	`spec-dock dashboard serve --port 18603 --offline --state-root <絶対の道> --tailscale` を立て、headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で写す。
	常駐のダッシュボード（47800）と道具の環境には触れない。
	"""

rollback: "PR を戻す（ダッシュボードの静的な資産とテストだけ）。古い保存の鍵は消さないので、戻すと版2の値で前の見え方に戻る。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実データの写しと試しの URL がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": {after: "S-03", range: "開始のコミット 16f0cf122 から S-03 の終わりまで", reviewer: "code-reviewer opus / medium", reason: "見せる範囲の判定と保存の移し替えが要。画面の変更の前に、ここで誤りを止める"}
	}
	final_quality_gate: {
		scope:          "開始のコミット 16f0cf122 から S-05 の終わりまで（S-06 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00603/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol": {task: "実装（S-01〜S-03）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。layout.js・prefs.js は DOM のない純粋な計算で node のテストで確かめられる（方針の「テストで確かめられる実装」× standard）。本人の指示で Sol を使う。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-ui":  {task: "実装（S-04〜S-05）", model: "opus", effort: "medium", rationale: "claude。道具の帯と見た目はフロントエンドの設計と実装（方針 × standard）"}
		owner:      {task: "実データの写しと試しの URL（S-06）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー（CP-1）", after: "S-03", model: "opus", effort: "medium"}
		gate: {role: "最終品質ゲート", after: "S-05", model: "opus", effort: "medium"}
	}
}
