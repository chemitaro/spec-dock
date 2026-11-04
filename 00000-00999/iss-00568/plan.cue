package spec

goal: "古さの判定を『最後に構造を確かめた時刻』にそろえる"

steps: {
	"S-01": {title: "確かめた時刻の関数と probe の読み取り（テスト先行）", realizes: ["R-01", "R-02", "F-01"], status: "done"}
	"S-02": {title: "モデル、summary、サーバー（署名を含む）に配線する", realizes: ["R-03", "R-04"], status: "done", after: ["S-01"]}
	"S-03": {title: "reference_cli.md と inventory を直す", realizes: ["R-04"], status: "done", after: ["S-02"]}
}

tests: {
	"T-01": {title: "純関数の表：新しい probe、古い probe、エラー付き、未来、不正", verifies: ["R-01", "R-02", "F-01"]}
	"T-02": {title: "probe.json がないか壊れているとき、build と summary が fetched_at で判定する", verifies: ["R-02", "F-01"]}
	"T-03": {title: "summary と API の fetched_at と stale が一致し、probe の更新が次の要求で反映する", verifies: ["R-03"]}
	"T-04": {title: "PR の状態と既存のテストが変わらない", verifies: ["R-04"]}
}

verification: "`make lint` と `uv run pytest`（全体）。"
execution: {
	sessions: impl: {task: "仕様化と実装", model: "sonnet", effort: "medium", rationale: "policy §4 light の実装"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "medium"}
		code: {role: "コードのレビュー", after: "S-03", model: "sonnet", effort: "high"}
	}
}
