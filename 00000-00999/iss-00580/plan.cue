package spec

steps: {
	"S-01": {title: "版を 0.9.0 にする", realizes: ["R-01"], status: "done", session: "impl"}
	"S-02": {title: "migration.md に 0.9.0 の節を足す（提供側と dogfood）", realizes: ["R-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "static-inventory.json と fixture とテストを足す", realizes: ["R-03"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "R-04 はマージの後に統括が行う", realizes: ["R-04"], status: "done", after: ["S-03"]}
}

tests: {
	"T-01": {title: "版が 0.9.0 の全部の場所でそろう", verifies: ["R-01"]}
	"T-02": {title: "migration.md に 0.9.0 の節と訂正があり、dogfood の写しと一致する", verifies: ["R-02"]}
	"T-03": {title: "inventory が 0.8.0 のバイトを知り、0.8.0 の consumer が installation update で上がる", verifies: ["R-03"]}
	"T-04": {title: "PR にタグも機能のコードの変更もない（差分の確認）", verifies: ["R-04"]}
}

execution: {
	sessions: impl: {task: "仕様化と実装", model: "sonnet", effort: "medium", rationale: "手本のあるリリースの手順で、版の番号と文書だけの変更。0.8.0 を入れ直せば戻る。"}
}
