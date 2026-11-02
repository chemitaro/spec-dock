package spec

// 計画（Issue）。型 specdock/v1。

goal: "`finalize-artifact.py` が版4の `spec-dock/initiatives` のリンクを通る Artifact を仕上げ、配布資産として更新で上がる。"

steps: {
	"S-01": {title: "リンク経路のテストを先に書く（Red）", realizes: ["R-01", "F-01"], status: "todo", session: "light"}
	"S-02": {title: "`_open_parent` を直す（Green）", realizes: ["R-01", "F-01"], status: "todo", after: ["S-01"], session: "light"}
	"S-03": {title: "インベントリと dogfood の写しを合わせ、更新のテストを書く", realizes: ["R-02"], status: "todo", after: ["S-02"], session: "light"}
}

tests: {
	"T-01": {title: "カタログへのリンクを通る Artifact を、identity と finalize で仕上げられる", verifies: ["R-01"]}
	"T-02": {title: "別の行き先、別のクローンのカタログ、名前だけが同じディレクトリ、`.git` のない worktree、リンクのカタログ、initiatives の下のリンク、Artifact のリンクは拒み、何も書かない", verifies: ["F-01"]}
	"T-03": {title: "0.5.0 の配布資産を持つリポジトリが `installation update` で上がり、`installation show` がすべて current になる", verifies: ["R-02"]}
}

verification: "`make lint` と `uv run pytest`（全体）を通す。仕様のレビュー opus/medium、コードのレビュー sonnet/high、最終品質ゲート opus/high（1人）。"
exit:         "PR がマージできる状態で、CI が通っている。"

execution: {
	sessions: light: {task: "仕様化と実装", model: "sonnet", effort: "medium", rationale: "policy §4 light の実装"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-03", model: "opus", effort: "medium"}
		code: {role: "コードのレビュー", after: "S-03", model: "sonnet", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "high"}
	}
}
