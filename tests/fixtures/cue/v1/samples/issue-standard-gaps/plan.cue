package spec

steps: {
	"S-01": {title: "保存を作る", realizes: ["R-01"], status: "done"}
	"S-02": {title: "削除を作る", realizes: ["R-02"], status: "doing", after: ["S-01"]}
	"S-03": {title: "掃除する", realizes: []}
}

tests: "T-01": {title: "保存できる", verifies: ["R-01"]}
