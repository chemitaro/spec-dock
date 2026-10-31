package spec

schema: "specdock/v1"

assurance: {
	level:  "critical"
	reason: "利用者のデータを消す処理で、戻せない"
}

requirements: "R-01": {
	title: "古い記録を消せる"
	acceptance: ["消した記録は、どの画面にも出ない"]
}

failures: {
	"F-01": {
		title:    "消す前に、写しを取る"
		impact:   "写しがないと戻せない"
		recovery: "写しから戻す"
	}
	"F-02": {
		title:    "途中で止まったら、消した分を報告する"
		impact:   "どこまで消えたか分からない"
		recovery: "報告をもとに、写しから戻す"
	}
}
