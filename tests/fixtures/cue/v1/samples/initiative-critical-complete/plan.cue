package spec

slices: {
	"epic-00021": {covers: ["R-01", "F-01"], session: "coord"}
	"epic-00022": {covers: ["R-02"], after: ["epic-00021"], session: "coord"}
}

rollback: "新しい保存先への書き込みを止め、古い保存先に戻す"

execution: {
	sessions: coord: {model: "opus", effort: "high"}
	reviews: gate: {after: "epic-00022"}
}
