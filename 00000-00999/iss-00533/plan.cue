package spec

// 計画（Issue）。型 specdock/v1。

goal: "Epic の D-10 のとおり、Markdown と PlantUML のダッシュボードの生成と付随の契約を撤去し、standard の検査（レビュー、lint、全体のテスト）を通した PR をマージできる状態で止める。"

steps: {
	"S-01": {title: "撤去を確かめる失敗するテスト（test_issue533）と wheel の一覧を足す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01", "F-02"], status: "done", session: "impl"}
	"S-02": {title: "生成のモジュールと同期の手順7、state.json の欄を消す", realizes: ["R-01", "R-04", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "canonical status の項目と canonical remove の手順、エラーの定数を消す", realizes: ["R-02", "R-03", "F-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-04": {title: "配布資産、文書、CLI の説明、inventory、dogfood の写しを直す", realizes: ["R-05"], status: "done", after: ["S-01"], session: "impl"}
	"S-05": {title: "古いテストと fixture を消し、既存のテストを直す", realizes: ["R-04"], status: "done", after: ["S-02", "S-03"], session: "impl"}
	"S-06": {title: "コードのレビュー、最終品質ゲート、report.md、PR と CI", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05"], status: "done", after: ["S-04", "S-05"], session: "impl"}
}

tests: {
	"T-01": {title: "2周の同期で5つのファイルができず、dashboards_written が0で、スナップショットは書かれる", verifies: ["R-01"]}
	"T-02": {title: "前の版が書いた5つのファイルを、同期が変えずに残す", verifies: ["R-01", "F-02"]}
	"T-03": {title: "canonical status の data に dashboard がなく、古い dashboard.error でも警告が出ない", verifies: ["R-02"]}
	"T-04": {title: "canonical remove の計画と結果に canonical.dashboard.remove がなく、5つのファイルが残る", verifies: ["R-03", "F-02"]}
	"T-05": {title: "壊れた dashboard の欄を持つ state.json が読め、次に書くと欄が消える", verifies: ["F-01"]}
	"T-06": {title: "4つのモジュールを import できず、src に生成の名前が現れず、新しい wheel に入らない", verifies: ["R-04"]}
	"T-07": {title: "配布する .gitignore と canonical.md、CLI の説明に5つのファイルの記述がなく、inventory と dogfood の写しが合う", verifies: ["R-05"]}
}

verification: "`uv run pytest tests/cli_runtime/test_issue533_dashboard_removal.py` を先に失敗させ（Red）、撤去の後に通す（Green）。最後に `make lint` と `uv run pytest`（全体）を同じコミットで通す。"
rollback:     "PR を戻せば、生成と契約は前の版に戻る。利用者の側は版を戻すと次の同期が5つのファイルを書き直す。"
exit:         "コードのレビューと最終品質ゲートの P0・P1 がなく、`make lint` と全体のテストが最終のコミットで通り、PR の CI が通ってマージできる状態。"

execution: {
	sessions: impl: {task: "仕様化と実装", model: "opus", effort: "medium", rationale: "epic-00427 の plan.cue の session std（policy §4 standard の実装）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-05", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-06", model: "opus", effort: "high"}
	}
}
