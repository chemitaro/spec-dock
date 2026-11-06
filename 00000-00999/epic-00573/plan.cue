package spec

// 計画（Epic）。型 specdock/v1。

goal: "状態の表し方と構造の図の配置を改め、0.9.0 として配る。"

slices: {
	"iss-00574": {
		covers: ["R-01", "R-02", "F-01"]
		text:   "状態の色と形、作業中の区切りの輪と30分の点滅、plan.cue の進み具合の API（PR #577）"
	}
	"iss-00575": {
		covers: ["R-03"]
		text:   "構造の図の最上位を、全体表示の倍率が最大になる行の幅で並べる（PR #576）"
	}
	"iss-00578": {
		covers: ["R-04"]
		text:   "構造の図の左右・上下の広い隙間と、枠の外への遠回りを直す（PR #579）"
	}
	"iss-00580": {
		covers: ["R-05"]
		text:   "SpecDock 0.9.0 のリリース（PR #582）"
		after: ["iss-00574", "iss-00575", "iss-00578"]
	}
}

verification: "各 Issue の report.md（ゲートの合格、headless Chrome の写し）と、統括のブラウザーでの確かめ。リリース後に7つのリポジトリで canonical check が合格する。"
exit:         "4つの子の Issue が閉じ、0.9.0 が7つのリポジトリに配られている。"
