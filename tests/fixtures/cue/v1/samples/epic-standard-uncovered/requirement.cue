package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "複数の Issue に分かれる通常の機能"
}

requirements: {
	"R-01": {title: "書き出せる", acceptance: ["書き出せる"]}
	"R-02": {title: "読み込める", acceptance: ["読み込める"]}
	"R-03": {title: "移せる", acceptance: ["別の PC で使える"]}
}
