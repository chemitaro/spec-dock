package spec

steps: {
	"S-01": {title: "写しを取る", realizes: ["F-01"], session: "impl"}
	"S-02": {title: "消す", realizes: ["R-01"], after: ["S-01"], session: "impl"}
	"S-03": {title: "準備", realizes: []}
}

tests: {
	"T-01": {title: "消せる", verifies: ["R-01"]}
	"T-02": {title: "写しがある", verifies: ["F-01"]}
}

execution: reviews: security: {role: "安全のレビュー", after: "S-04"}
