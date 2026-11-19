package spec

// 要件（Epic）。型 specdock/v1。

schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "構造の図の帯の役割と、worktree の見つけ方を変える"
}

purpose: """
	構造の図と『横断の構造』で、(1) 統括が居る主のワークスペース（main のチェックアウト）がいつも図に出続け、(2) どの Scope にも紐づかない worktree（work start していない作業）にすぐ気づけるようにする。
	この Epic は Issue iss-00668 の1つだけを持つ（統括の依頼書、2026-11-19）。
	"""

requirements: {
	"R-01": {
		title: "主のチェックアウトが、誰も指揮していなくても、両方の画面にいつも出る"
		acceptance: ["iss-00668 の R-02・R-07 の受入が満たされる"]
	}
	"R-02": {
		title: "どの Scope にも紐づかない worktree が、git の一覧を土台に、見方ごとの決まりで出る"
		acceptance: ["iss-00668 の R-01・R-03・R-04・R-05・R-06 の受入が満たされる"]
	}
	"R-03": {
		title: "線の検査と重さが戻らない"
		acceptance: ["iss-00668 の R-08 の受入が満たされる"]
	}
}

failures: {
	"F-01": {title: "git の一覧や Orca の要約が読めないときも、画面は今の帯の扱いを下回らない（iss-00668 F-01・F-02）"}
}

decisions: [
	"2026-11-19 本人と統括：決定の正本は iss-00668 の requirement.cue の decisions（行の名前 Unscoped、印 Primary・Unlinked、『これから』で線を引かない、など）",
]
