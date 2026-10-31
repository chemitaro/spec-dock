package spec

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "通常の機能の追加"
}

requirements: {
	"R-01": {
		title: "値を保存できる"
		text: """
			保存した値は、**次に開いたとき**にも読める。
			"""
		acceptance: ["保存した値を、開き直した後に読める"]
	}
	"R-02": {
		title: "値を消せる"
		acceptance: ["消した値は読めない"]
	}
}

failures: "F-01": title: "壊れた入力は保存しない"
