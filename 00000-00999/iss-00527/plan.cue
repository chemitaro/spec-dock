package spec

goal: "試しの仕組みを作り、PC の Chrome（と手に入れば Safari）で確かめ、結果を report.md に書く。"

steps: {
	"S-01": {title: "試しの仕組み（サーバーと HTML）を書く", realizes: ["R-01", "R-02", "R-03"], status: "doing", session: "impl"}
	"S-02": {title: "PC の Chrome で項目ごとに確かめる", realizes: ["R-01", "R-02", "R-03"], after: ["S-01"], session: "impl"}
	"S-03": {title: "report.md と iPhone の手順を書く", realizes: ["R-04"], after: ["S-02"], session: "impl"}
	"S-04": {title: "サーバーと Chrome を止める", realizes: ["F-01"], after: ["S-02"], session: "impl"}
}

tests: {
	"T-01": {title: "項目ごとの結果が report.md の表にある", verifies: ["R-01", "R-02", "R-03", "R-04"]}
	"T-02": {title: "試しのプロセスが残っていない（lsof で確かめる）", verifies: ["F-01"]}
}

execution: sessions: impl: {task: "試作と確かめ", model: "sonnet", effort: "medium", rationale: "policy §4 light"}
