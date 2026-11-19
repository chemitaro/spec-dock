package spec

// 計画（Epic）。型 specdock/v1。

goal: "iss-00668 の1つの Issue で Epic の要件を満たす"

slices: {
	"iss-00668": {
		covers: ["R-01", "R-02", "R-03", "F-01"]
		text:   "Unscoped の行、git の worktree の一覧、見方ごとの出し方、実機の確かめと移行の案内"
	}
}

exit: "iss-00668 の PR がマージされ、Issue が閉じる。"
