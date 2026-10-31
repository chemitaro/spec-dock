package spec

steps: {
	"S-01": {title: "書き出しを作る", realizes: ["R-01"], status: "done", session: "impl"}
	"S-02": {title: "上書きを止める", realizes: ["F-01"], status: "doing", after: ["S-01"], session: "impl"}
	"S-03": {title: "古い案", realizes: [], status: "dropped"}
}

tests: {
	"T-01": {title: "書き出して読み込める", verifies: ["R-01"]}
	"T-02": {title: "既にあるときは止まる", verifies: ["F-01"]}
}

verification: "`uv run pytest`"
exit:         "PR がマージできる状態"

execution: {
	sessions: impl: {task: "仕様化と実装", model: "opus", effort: "high", rationale: "strict の Issue"}
	reviews: code: {role: "コードのレビュー", after: "S-02", model: "opus", effort: "high"}
}
